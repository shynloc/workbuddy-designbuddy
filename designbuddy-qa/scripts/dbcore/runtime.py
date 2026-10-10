"""Runtime self-checks shared by the commercial build and the QA runner.

Environment report, package fingerprint/integrity and installed-copy extras.
Standard library only. Read-only: nothing in this module writes files.
"""
import os
import platform
import shutil
import sys
from pathlib import Path

from .util import DESIGNBUDDY_VERSION, SCHEMA_VERSION, SKILL_NAME, SKILL_ROOT, TEMPLATES, now_iso, read_json, sha256_bytes

# Files the WorkBuddy client adds to an installed skill root. OBSERVED: WorkBuddy 5.7.7.0 / Windows 11
# writes `_user_meta.json` at install time. Only the file NAME is checked; its content is never read.
PLATFORM_META = {"_user_meta.json"}


# ---------------------------------------------------------------- environment & package

def _child_env():
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def environment():
    tools = {n: bool(shutil.which(n)) for n in ("python3", "python", "py", "node", "bash", "zsh", "pwsh", "powershell")}
    shell = {k: (Path(os.environ[k]).name if k in ("SHELL", "COMSPEC") else "present") if k in os.environ else None
             for k in ("SHELL", "COMSPEC", "PSModulePath", "MSYSTEM", "TERM_PROGRAM")}
    return {"designbuddy": DESIGNBUDDY_VERSION, "skill": SKILL_NAME, "schema_version": SCHEMA_VERSION,
            "os": sys.platform, "platform": platform.platform(), "machine": platform.machine(),
            "python": {"version": platform.python_version(), "implementation": platform.python_implementation()},
            "tools_on_path": tools, "shell_hints": shell, "cwd": str(Path.cwd()), "skill_root": str(SKILL_ROOT),
            "fs_encoding": sys.getfilesystemencoding(), "workbuddy_version": "UNKNOWN（由 Agent 记录：ENV-007）",
            "package": package_fingerprint(), "captured_at": now_iso()}


def package_fingerprint():
    """Ties a report to a release: version + SHA-256 of templates/package-manifest.json."""
    man = TEMPLATES / "package-manifest.json"
    if not man.is_file():
        return {"version": DESIGNBUDDY_VERSION, "manifest_sha256": None, "note": "开发源码（未打包）"}
    data = read_json(man)
    return {"version": data.get("version"), "manifest_sha256": sha256_bytes(man.read_bytes()), "files": len(data.get("files", {}))}


def installed_extras():
    """Files present in the installed skill but not in the package manifest, classified."""
    man = TEMPLATES / "package-manifest.json"
    if not man.is_file():
        return None
    listed = set(read_json(man)["files"]) | {"templates/package-manifest.json"}
    platform, unknown = [], []
    for p in sorted(SKILL_ROOT.rglob("*")):
        if not p.is_file() or "__pycache__" in p.parts:
            continue
        rel = p.relative_to(SKILL_ROOT).as_posix()
        if rel in listed:
            continue
        (platform if rel in PLATFORM_META else unknown).append(rel)
    return {"platform": platform, "unknown": unknown}


def package_integrity():
    man_path = TEMPLATES / "package-manifest.json"
    if not man_path.is_file():
        return {"ok": False, "reason": "templates/package-manifest.json 不存在（开发源码未经打包）", "mismatch": [], "missing": []}
    man = read_json(man_path)
    mismatch, missing = [], []
    for rel, want in man["files"].items():
        p = SKILL_ROOT / rel
        if not p.is_file():
            missing.append(rel)
        elif sha256_bytes(p.read_bytes()) != want:
            mismatch.append(rel)
    return {"ok": not mismatch and not missing, "version": man.get("version"), "files": len(man["files"]),
            "mismatch": mismatch, "missing": missing}


