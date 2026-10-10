"""Shared helpers: JSON I/O, safe paths, hashing, escaping, redaction.

Standard library only (Python >= 3.8).
"""
import datetime as _dt
import hashlib
import html
import json
import os
import re
from pathlib import Path

DESIGNBUDDY_VERSION = "0.1.3"
SKILL_NAME = "designbuddy-qa"
SCHEMA_VERSION = "1.0.0"

SKILL_ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATES = SKILL_ROOT / "templates"

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
RULE_ID_RE = re.compile(r"^(MUST|SHOULD|AVOID|NEVER)-[A-Z][A-Z0-9]*-\d{2}$")
CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")


class DBError(Exception):
    """User-facing error with a stable code. Never carries a traceback to the user."""

    def __init__(self, code, message, detail=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.detail = detail or {}

    def as_dict(self):
        return {"ok": False, "error": {"code": self.code, "message": self.message, "detail": self.detail}}


def now_iso():
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch and epoch.isdigit():
        return _dt.datetime.fromtimestamp(int(epoch), _dt.timezone.utc).isoformat(timespec="seconds")
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def read_json(path):
    p = Path(path)
    try:
        raw = p.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        raise DBError("E_NOT_FOUND", "文件不存在：%s" % p.name)
    except UnicodeDecodeError:
        raise DBError("E_ENCODING", "文件不是 UTF-8 文本：%s" % p.name)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise DBError("E_INVALID_JSON", "JSON 格式错误：%s（第 %d 行第 %d 列）" % (p.name, e.lineno, e.colno))


def dump_json(data):
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def write_text(path, text):
    """Write UTF-8 with LF line endings regardless of OS (reproducible bytes)."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(text.replace("\r\n", "\n").encode("utf-8"))
    return p


def write_json(path, data):
    return write_text(path, dump_json(data))


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    return sha256_bytes(Path(path).read_bytes())


def canonical(data):
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def esc_html(s):
    return html.escape(str(s), quote=True)


def esc_md(s):
    """Neutralise characters that would break Markdown tables or inject HTML."""
    s = str(s).replace("|", "\\|")
    return html.escape(s, quote=False)


def inert(s):
    """Make text inert for places that may be rendered as HTML (frontmatter, YAML)."""
    return str(s).replace("<", "\uff1c").replace(">", "\uff1e")


def yaml_str(s):
    """Double-quoted YAML scalar with angle brackets neutralised. Control chars are rejected upstream."""
    s = inert(s).replace("\\", "\\\\").replace('"', '\\"')
    return '"%s"' % s


def safe_text(value, field, max_len=200):
    if not isinstance(value, str) or not value.strip():
        raise DBError("E_FIELD", "字段 %s 必须是非空文本" % field)
    if CONTROL_RE.search(value):
        raise DBError("E_FIELD", "字段 %s 含有换行或控制字符" % field)
    if len(value) > max_len:
        raise DBError("E_FIELD", "字段 %s 超过 %d 个字符" % (field, max_len))
    return value.strip()


FONT_NAME_RE = re.compile(r"^[\w\u4e00-\u9fff\u3400-\u4dbf ()（）.+&-]{1,60}$")
RADIUS_RE = re.compile(r"^(0|\d{1,3}(\.\d{1,2})?(px|rem))$")


def safe_font_name(value, field="font"):
    """Font names end up inside CSS/HTML; allow a conservative character set only."""
    value = safe_text(value, field, 60)
    if not FONT_NAME_RE.match(value):
        raise DBError("E_FONT_NAME", "字体名 %s 含有不允许的字符：%r" % (field, value))
    return value


def safe_radius(value, field="radius"):
    value = safe_text(str(value), field, 12)
    if not RADIUS_RE.match(value):
        raise DBError("E_FIELD", "%s 必须形如 8px / 0.5rem / 0：%r" % (field, value))
    return value


def safe_weight(value, field="heading_weight"):
    try:
        w = int(value)
    except (TypeError, ValueError):
        raise DBError("E_FIELD", "%s 必须是 100–900 的整数" % field)
    if w < 100 or w > 900 or w % 100:
        raise DBError("E_FIELD", "%s 必须是 100–900 的整百数" % field)
    return w


def safe_relpath(rel, field="path"):
    """Reject absolute paths, drive letters, traversal and odd separators."""
    if not isinstance(rel, str) or not rel:
        raise DBError("E_PATH", "%s 不能为空" % field)
    if CONTROL_RE.search(rel) or "\\" in rel or rel.startswith("/") or re.match(r"^[A-Za-z]:", rel):
        raise DBError("E_PATH", "%s 必须是相对路径：%s" % (field, rel))
    parts = rel.split("/")
    if any(p in ("", ".", "..") for p in parts):
        raise DBError("E_PATH", "%s 含有不安全的路径片段：%s" % (field, rel))
    return rel


def resolve_inside(base, rel, field="path"):
    base = Path(base).resolve()
    target = (base / safe_relpath(rel, field)).resolve()
    if base != target and base not in target.parents:
        raise DBError("E_PATH", "%s 越出了允许的目录：%s" % (field, rel))
    return target


_GENERIC_HOME = [
    re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+[^\\/\s\"'<>|]+", re.I),      # Windows user homes, any slash or case
    re.compile(r"(?<![\w.])/(?:Users|home)/[^/\s\"'<>|]+"),                     # POSIX user homes (macOS, Linux)
]


def _path_variants(p):
    p = str(p)
    if not p or p in ("/", "\\"):
        return []
    fwd = p.replace("\\", "/")
    back = p.replace("/", "\\")
    return sorted({p, fwd, back, back.replace("\\", "\\\\")}, key=len, reverse=True)


def _username():
    for k in ("USERNAME", "USER", "LOGNAME"):
        v = os.environ.get(k)
        if v and len(v) >= 3:
            return v
    name = Path.home().name
    return name if len(name) >= 3 else None


def redact(text, extra=None):
    """Replace machine-specific paths with placeholders.

    Handles Windows and POSIX forms, forward/back slashes, JSON-escaped
    backslashes and drive-letter case, then any remaining user-home pattern
    and the account name as a path segment.
    """
    out = str(text)
    pairs = [(v, k) for k, v in (extra or {}).items() if v]
    pairs.append((str(Path.home()), "<HOME>"))
    expanded = []
    for val, key in pairs:
        for var in _path_variants(val):
            expanded.append((var, key))
    for var, key in sorted(expanded, key=lambda kv: -len(kv[0])):
        out = re.sub(re.escape(var), lambda _m, key=key: key, out, flags=re.I)
    for rx in _GENERIC_HOME:
        out = rx.sub("<HOME>", out)
    user = _username()
    if user:
        out = re.sub(r"(?<=[\\/])%s(?=[\\/])" % re.escape(user), "<USER>", out, flags=re.I)
    return out


def redact_obj(obj, extra=None):
    """Apply redact() to every string inside a JSON-like structure."""
    if isinstance(obj, str):
        return redact(obj, extra)
    if isinstance(obj, list):
        return [redact_obj(x, extra) for x in obj]
    if isinstance(obj, dict):
        return {k: redact_obj(v, extra) for k, v in obj.items()}
    return obj


def leaks(text, extra=None):
    """Return the list of path fragments that redact() should have removed."""
    found = []
    for val in [str(Path.home())] + [str(v) for v in (extra or {}).values() if v]:
        for var in _path_variants(val):
            if re.search(re.escape(var), text, flags=re.I):
                found.append(var)
    for rx in _GENERIC_HOME:
        found += rx.findall(text)
    user = _username()
    if user and re.search(r"(?<=[\\/])%s(?=[\\/])" % re.escape(user), text, flags=re.I):
        found.append("<username as path segment>")
    return sorted(set(found))


def render(template_text, mapping):
    """Minimal `{{key}}` substitution. Values must already be escaped for their context."""
    def sub(m):
        key = m.group(1)
        if key not in mapping:
            raise DBError("E_TEMPLATE", "模板变量缺失：%s" % key)
        return str(mapping[key])
    return re.sub(r"\{\{\s*([a-zA-Z0-9_.]+)\s*\}\}", sub, template_text)


def load_template(rel):
    p = TEMPLATES / rel
    try:
        return p.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise DBError("E_TEMPLATE", "模板缺失：%s" % rel)
