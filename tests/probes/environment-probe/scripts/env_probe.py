#!/usr/bin/env python3
"""DesignBuddy environment probe (dbprobe-environment).

Standard library only. Python >= 3.8. Read-only except for files written
under the results directory (default: <cwd>/dbprobe-results/). Never sends
data anywhere.

Usage:
    python3 env_probe.py [--out DIR] [--font "Source Han Sans"] [--font ...]
"""
import argparse
import datetime as _dt
import json
import os
import platform
import shutil
import sys
import tempfile
import uuid
import zipfile
from pathlib import Path

PROBE = "dbprobe-environment"
PROBE_VERSION = "1.0.0"
REF_MARKER = "DBP-ENV-REF-5K2P"
TPL_MARKER = "DBP-ENV-TPL-8V3N"

SKILL_DIR = Path(__file__).resolve().parent.parent

# Only the presence of these variables is recorded, plus the basename of a
# few shell-related values. No other environment values leave the machine.
SHELL_VARS = ["SHELL", "COMSPEC", "PSModulePath", "MSYSTEM", "TERM_PROGRAM", "WSL_DISTRO_NAME"]

FONT_DIRS = {
    "darwin": ["/System/Library/Fonts", "/Library/Fonts", "~/Library/Fonts"],
    "windows": ["%WINDIR%/Fonts", "%LOCALAPPDATA%/Microsoft/Windows/Fonts"],
    "linux": ["/usr/share/fonts", "/usr/local/share/fonts", "~/.local/share/fonts", "~/.fonts"],
}


def now():
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


class Report:
    def __init__(self):
        self.checks = []

    def add(self, cid, capability, result, detail):
        self.checks.append({"id": cid, "capability": capability, "result": result, "detail": detail})


def os_family():
    p = sys.platform
    if p.startswith("win"):
        return "windows"
    if p == "darwin":
        return "darwin"
    if p.startswith("linux"):
        return "linux"
    return p


def check_interpreter(rep):
    rep.add("ENV-PY", "Python interpreter runs this script", "PASS", {
        "executable": sys.executable,
        "version": platform.python_version(),
        "implementation": platform.python_implementation(),
        "ok_for_designbuddy": sys.version_info >= (3, 8),
    })


def check_platform(rep):
    rep.add("ENV-OS", "Operating system", "PASS", {
        "os_family": os_family(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "filesystem_encoding": sys.getfilesystemencoding(),
        "stdout_encoding": getattr(sys.stdout, "encoding", None),
    })


def check_shell_hints(rep):
    hints = {}
    for k in SHELL_VARS:
        v = os.environ.get(k)
        if v is None:
            hints[k] = None
        elif k in ("SHELL", "COMSPEC"):
            hints[k] = Path(v).name
        else:
            hints[k] = "present"
    rep.add("ENV-SHELL", "Shell hints visible to child process", "PASS", hints)


def check_tools(rep):
    tools = {}
    for name in ["python3", "python", "py", "node", "bash", "zsh", "sh", "pwsh", "powershell", "cmd", "git"]:
        found = shutil.which(name)
        tools[name] = found is not None
    rep.add("ENV-TOOLS", "Commands found on PATH (presence only)", "PASS", tools)


def check_paths(rep):
    cwd = Path.cwd()
    rep.add("ENV-PATHS", "Working directory and skill location", "PASS", {
        "cwd": str(cwd),
        "script_path": str(Path(__file__).resolve()),
        "skill_dir": str(SKILL_DIR),
        "skill_dir_is_under_cwd": str(SKILL_DIR).startswith(str(cwd)),
    })


def check_own_files(rep):
    targets = {
        "references/env-reference.md": REF_MARKER,
        "templates/env-template.txt": TPL_MARKER,
    }
    detail = {}
    ok = 0
    for rel, marker in targets.items():
        p = SKILL_DIR / rel
        try:
            text = p.read_text(encoding="utf-8")
            found = marker in text
            detail[rel] = "marker found" if found else "readable, marker missing"
            ok += 1 if found else 0
        except Exception as e:  # noqa: BLE001 - report every failure verbatim
            detail[rel] = "unreadable: %s: %s" % (type(e).__name__, e)
    result = "PASS" if ok == len(targets) else ("PARTIAL" if ok else "FAIL")
    rep.add("ENV-SELFREAD", "Script reads files inside its own skill package", result, detail)


def check_write(rep, out_dir):
    detail = {"out_dir": str(out_dir)}
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        p = out_dir / ("write-test-%s.txt" % uuid.uuid4().hex[:8])
        payload = "DesignBuddy 写入测试 ✓"
        p.write_text(payload, encoding="utf-8")
        back = p.read_text(encoding="utf-8")
        p.unlink()
        detail["roundtrip"] = back == payload
        result = "PASS" if back == payload else "FAIL"
    except Exception as e:  # noqa: BLE001
        detail["error"] = "%s: %s" % (type(e).__name__, e)
        result = "FAIL"
    rep.add("ENV-WRITE", "Write/read/delete a UTF-8 file in the results directory", result, detail)


def check_unicode_path(rep, out_dir):
    detail = {}
    try:
        d = out_dir / "中文 目录 test"
        d.mkdir(parents=True, exist_ok=True)
        f = d / "品牌 文件.json"
        f.write_text(json.dumps({"名称": "测试"}, ensure_ascii=False), encoding="utf-8")
        data = json.loads(f.read_text(encoding="utf-8"))
        f.unlink()
        d.rmdir()
        detail["roundtrip"] = data == {"名称": "测试"}
        result = "PASS" if detail["roundtrip"] else "FAIL"
    except Exception as e:  # noqa: BLE001
        detail["error"] = "%s: %s" % (type(e).__name__, e)
        result = "FAIL"
    rep.add("ENV-UNICODE-PATH", "Chinese characters and spaces in paths", result, detail)


def check_zip(rep, out_dir):
    detail = {}
    try:
        zp = out_dir / "zip-test.zip"
        with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("probe-skill/SKILL.md", "---\nname: x\n---\n中文\n")
        with zipfile.ZipFile(zp) as z:
            names = z.namelist()
            body = z.read("probe-skill/SKILL.md").decode("utf-8")
        zp.unlink()
        detail["names"] = names
        result = "PASS" if "中文" in body else "FAIL"
    except Exception as e:  # noqa: BLE001
        detail["error"] = "%s: %s" % (type(e).__name__, e)
        result = "FAIL"
    rep.add("ENV-ZIP", "Create and read a ZIP with stdlib zipfile", result, detail)


def check_temp(rep):
    try:
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / "a.txt").write_text("ok", encoding="utf-8")
        rep.add("ENV-TEMP", "System temp directory usable", "PASS", {})
    except Exception as e:  # noqa: BLE001
        rep.add("ENV-TEMP", "System temp directory usable", "FAIL", {"error": str(e)})


def check_fonts(rep, queries):
    """Look only for the font families the tester named, by filename.

    Lists the standard font directories but records nothing except the
    number of matching files per query. Never copies font files.
    """
    if not queries:
        rep.add("ENV-FONT", "Named font presence check", "NOT_TESTED", {"reason": "no --font given"})
        return
    dirs = []
    for raw in FONT_DIRS.get(os_family(), []):
        p = Path(os.path.expandvars(os.path.expanduser(raw)))
        if p.is_dir():
            dirs.append(p)
    detail = {"searched_dirs": [str(d) for d in dirs], "matches": {}}
    for q in queries:
        key = q.lower().replace(" ", "")
        count = 0
        for d in dirs:
            for root, _dirs, files in os.walk(d):
                for fn in files:
                    if key in fn.lower().replace(" ", "").replace("-", ""):
                        count += 1
        detail["matches"][q] = count
    detail["note"] = "Filename match only; family names inside font files are not read (EXPERIMENTAL)."
    rep.add("ENV-FONT", "Named font presence check", "PARTIAL" if dirs else "FAIL", detail)


def write_outputs(rep, out_dir, started):
    run_id = "env-%s-%s" % (_dt.datetime.now().strftime("%Y%m%d-%H%M%S"), uuid.uuid4().hex[:4])
    payload = {
        "probe": PROBE,
        "probe_version": PROBE_VERSION,
        "run_id": run_id,
        "started_at": started,
        "finished_at": now(),
        "runner": "python",
        "checks": rep.checks,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    jp = out_dir / (run_id + ".json")
    jp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    payload["result_file"] = str(jp)
    return payload


def print_summary(payload):
    print("=== DBPROBE REPORT BEGIN ===")
    print("probe: %s %s" % (payload["probe"], payload["probe_version"]))
    print("run_id: %s" % payload["run_id"])
    print("result_file: %s" % payload.get("result_file"))
    for c in payload["checks"]:
        print("- [%s] %s — %s" % (c["result"], c["id"], c["capability"]))
        print("    %s" % json.dumps(c["detail"], ensure_ascii=False))
    print("=== DBPROBE REPORT END ===")


def main():
    try:  # Windows consoles may not be UTF-8; never crash on printing
        sys.stdout.reconfigure(errors="replace")
    except Exception:  # noqa: BLE001
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None, help="results directory (default: <cwd>/dbprobe-results)")
    ap.add_argument("--font", action="append", default=[], help="font family to look for (repeatable)")
    args = ap.parse_args()
    started = now()
    out_dir = Path(args.out) if args.out else Path.cwd() / "dbprobe-results"
    rep = Report()
    for fn in (check_interpreter, check_platform, check_shell_hints, check_tools, check_paths, check_own_files, check_temp):
        fn(rep)
    check_write(rep, out_dir)
    check_unicode_path(rep, out_dir)
    check_zip(rep, out_dir)
    check_fonts(rep, args.font)
    try:
        payload = write_outputs(rep, out_dir, started)
    except Exception as e:  # noqa: BLE001
        payload = {"probe": PROBE, "probe_version": PROBE_VERSION, "run_id": "unsaved",
                   "result_file": "NOT SAVED: %s" % e, "checks": rep.checks}
    print_summary(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
