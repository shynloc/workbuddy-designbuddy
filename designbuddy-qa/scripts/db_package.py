"""Skill package lint and deterministic ZIP packing (WorkBuddy skill layout)."""
import re
import zipfile
from pathlib import Path

from db_util import SLUG_RE, sha256_bytes

REQUIRED_FM = ("description", "description_zh", "description_en", "version", "author")
ALLOWED_TOP = {"SKILL.md", "references", "scripts", "templates"}
FONT_EXT = {".ttf", ".otf", ".woff", ".woff2", ".ttc", ".eot"}
TEXT_EXT = {".md", ".py", ".json", ".css", ".html", ".svg", ".txt", ".tmpl", ".js"}
FIXED_TIME = (2026, 1, 1, 0, 0, 0)
_HOME_ROOTS = ("/" + "home/", "/" + "Users/")  # split so this file does not match its own lint
ABS_PATH_RE = re.compile(r"(?<![\w.])(%s[^\s'\"<>]+|%s[A-Za-z][^\s'\"<>]*|[A-Z]:\\\\Users\\\\[^\s'\"]+)" % _HOME_ROOTS)
SECRET_RE = re.compile(r"(api[_-]?key|secret|access[_-]?token|password)\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]", re.I)
REF_RE = re.compile(r"@references/([^\s`|)]+)")
SVG_BAD = re.compile(r"<script|\son[a-z]+\s*=|javascript:|<foreignObject", re.I)


def parse_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text.replace("\r\n", "\n"), re.S)
    if not m:
        return None
    fm = {}
    for line in m.group(1).splitlines():
        mm = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not mm:
            continue
        val = mm.group(2).strip()
        if len(val) >= 2 and val[0] == val[-1] == '"':
            val = val[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        fm[mm.group(1)] = val
    return fm


def lint_skill(root, platform_files=()):
    """Return {"errors": [...], "warnings": [...], "frontmatter": {...}, "files": n, "platform_files": [...]}.

    platform_files: names the WorkBuddy client is OBSERVED to add to an installed
    skill root (e.g. `_user_meta.json`). They are reported, never read, and are
    not package errors. Release builds pass no platform_files, so our own ZIP
    can never contain them.
    """
    root = Path(root)
    errors, warnings = [], []
    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        return {"errors": ["缺少 SKILL.md"], "warnings": [], "frontmatter": None, "files": 0}
    text = skill_md.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    if fm is None:
        errors.append("SKILL.md frontmatter 无法解析")
        fm = {}
    for k in REQUIRED_FM:
        if not fm.get(k):
            errors.append("frontmatter 缺少必填字段 %s" % k)
    if fm.get("version") and not re.fullmatch(r"\d+\.\d+\.\d+", fm["version"]):
        errors.append("version 不是 SemVer：%s" % fm["version"])
    if fm.get("name") and not SLUG_RE.match(fm["name"]):
        errors.append("name 不是 kebab-case：%s" % fm["name"])
    if fm.get("name") and fm["name"] != root.name:
        warnings.append("目录名 %s 与 frontmatter name %s 不一致" % (root.name, fm["name"]))
    platform = []
    for p in root.iterdir():
        if p.name in platform_files and p.is_file():
            platform.append(p.name)
        elif p.name not in ALLOWED_TOP:
            errors.append("根目录存在非标准项：%s" % p.name)
    for m in REF_RE.finditer(text):
        ref = m.group(1)
        clean = re.sub(r"[，。；、：）)]+$", "", ref)
        if clean != ref:
            errors.append("@references/%s 后紧跟标点，请在路径后加空格" % clean)
        if not (root / "references" / clean).is_file():
            errors.append("引用的文件不存在：references/%s" % clean)
    n = 0
    total = 0
    for p in sorted(root.rglob("*")):
        if not p.is_file() or "__pycache__" in p.parts:
            continue
        if p.parent == root and p.name in platform:
            continue
        n += 1
        rel = p.relative_to(root).as_posix()
        if rel.count("/") > 1:
            # OBSERVED (WorkBuddy 开放平台解析器, 2026-10-11): 只支持 根目录/二级目录/文件 两级结构
            errors.append("目录层级超限（仅支持 根目录/二级目录/文件）：%s" % rel)
        data = p.read_bytes()
        total += len(data)
        if p.suffix.lower() in FONT_EXT:
            errors.append("包内不允许字体文件：%s" % rel)
        if p.name in (".DS_Store", "Thumbs.db") or p.name.startswith("._"):
            errors.append("包内有系统垃圾文件：%s" % rel)
        if p.suffix.lower() in TEXT_EXT:
            body = data.decode("utf-8", errors="replace")
            if ABS_PATH_RE.search(body):
                errors.append("包含本地绝对路径：%s" % rel)
            if SECRET_RE.search(body):
                errors.append("疑似包含密钥：%s" % rel)
            if p.suffix.lower() == ".svg" and SVG_BAD.search(body):
                errors.append("SVG 含有脚本或事件属性：%s" % rel)
    if total > 5 * 1024 * 1024:
        warnings.append("包体超过 5MB（%d bytes）" % total)
    return {"errors": errors, "warnings": warnings, "frontmatter": fm, "files": n, "bytes": total, "platform_files": platform}


def pack(root, zip_path, root_name=None):
    """Deterministic ZIP with exactly one top-level directory."""
    root = Path(root)
    root_name = root_name or root.name
    zip_path = Path(zip_path)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(root.rglob("*")):
            if not p.is_file() or "__pycache__" in p.parts or p.name == ".DS_Store":
                continue
            info = zipfile.ZipInfo("%s/%s" % (root_name, p.relative_to(root).as_posix()), FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, p.read_bytes())
    return zip_path, sha256_bytes(zip_path.read_bytes())


def zip_roots(zip_path):
    with zipfile.ZipFile(zip_path) as z:
        return sorted({n.split("/", 1)[0] for n in z.namelist()})
