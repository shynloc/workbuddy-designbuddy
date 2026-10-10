#!/usr/bin/env python3
"""Lint and pack every probe into tests/probes/dist/<skill-name>-<version>.zip.

Each ZIP has exactly one top-level directory named after the skill's
frontmatter `name`, as the WorkBuddy skill spec expects. Standard library only.

    python3 tests/probes/tools/pack_probes.py
"""
import hashlib
import re
import sys
import zipfile
from pathlib import Path

PROBES = Path(__file__).resolve().parent.parent
DIST = PROBES / "dist"
FOLDERS = ["environment-probe", "installation-probe", "protection-probe", "brand-alpha", "brand-beta"]
REQUIRED = ["description", "description_zh", "description_en", "version", "author"]
ALLOWED_TOP = {"SKILL.md", "references", "scripts", "templates"}
# Zip timestamps are pinned so rebuilding unchanged sources gives identical bytes.
FIXED_TIME = (2026, 1, 1, 0, 0, 0)


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm


def lint(folder):
    root = PROBES / folder
    errors = []
    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        return None, ["missing SKILL.md"]
    text = skill_md.read_text(encoding="utf-8")
    fm = frontmatter(text)
    if fm is None:
        return None, ["frontmatter not parseable"]
    for k in REQUIRED:
        if not fm.get(k):
            errors.append("missing frontmatter field: %s" % k)
    if not re.fullmatch(r"\d+\.\d+\.\d+", fm.get("version", "")):
        errors.append("version is not SemVer")
    for p in root.iterdir():
        if p.name not in ALLOWED_TOP:
            errors.append("non-standard top-level entry: %s" % p.name)
    for ref in set(re.findall(r"@references/([\w./-]+\.md)", text)):
        if not (root / "references" / ref).is_file():
            errors.append("missing reference: %s" % ref)
    for p in root.rglob("*"):
        if p.is_file() and p.suffix in {".md", ".py", ".js", ".json", ".txt", ".html"}:
            body = p.read_text(encoding="utf-8")
            if re.search(r"(/home/|/Users/[A-Za-z]|[A-Z]:\\\\Users\\\\)", body):
                errors.append("absolute user path in %s" % p.relative_to(root))
            if re.search(r"(api[_-]?key|secret|token)\s*[:=]\s*['\"][A-Za-z0-9]{16,}", body, re.I):
                errors.append("possible secret in %s" % p.relative_to(root))
    return fm, errors


def pack(folder, fm):
    root = PROBES / folder
    name, version = fm["name"], fm["version"]
    DIST.mkdir(exist_ok=True)
    zp = DIST / ("%s-%s.zip" % (name, version))
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(root.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts and p.name != ".DS_Store":
                info = zipfile.ZipInfo("%s/%s" % (name, p.relative_to(root).as_posix()), FIXED_TIME)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                z.writestr(info, p.read_bytes())
    return zp


def main():
    failed = False
    sums = []
    for folder in FOLDERS:
        fm, errors = lint(folder)
        if errors:
            failed = True
            print("[FAIL] %s" % folder)
            for e in errors:
                print("    - %s" % e)
            continue
        zp = pack(folder, fm)
        digest = hashlib.sha256(zp.read_bytes()).hexdigest()
        sums.append("%s  %s" % (digest, zp.name))
        print("[PASS] %s -> dist/%s" % (folder, zp.name))
    if sums:
        (DIST / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
