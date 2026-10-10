#!/usr/bin/env python3
"""DesignBuddy installation probe — deterministic mini compiler.

Generates a tiny, harmless skill named `dbprobe-generated-hello` from data
embedded in this file (no template copying), plus a build manifest with
SHA-256 hashes so the installed copy can later verify itself byte-for-byte.

Standard library only. Writes only under <cwd>/dbprobe-results/generated/.

Usage:
    python3 gen_skill.py [--version 1.0.0|1.1.0] [--out DIR]
"""
import argparse
import datetime as _dt
import hashlib
import json
import sys
import uuid
import zipfile
from pathlib import Path

SKILL_NAME = "dbprobe-generated-hello"
GENERATOR = "dbprobe-installation 1.0.0"

# Each version has a different "brand rule" value so an upgrade is observable.
VARIANTS = {
    "1.0.0": {"color": "#2F6FEB", "marker": "DBP-GEN-100-A7"},
    "1.1.0": {"color": "#0F7B5F", "marker": "DBP-GEN-110-C4"},
}

SKILL_MD = """---
name: {name}
display_name: DesignBuddy 安装验证样品
display_name_en: DesignBuddy Install Verification Sample
description: DesignBuddy 开发测试专用。仅当用户明确说“运行 DesignBuddy 安装验证”或“run dbprobe install verify”时使用；核对本 Skill 安装后的文件、规则与版本是否与原始构建一致。不要在其他任何场景使用。
description_zh: DesignBuddy 开发测试专用：核对安装后的 Skill 与原始构建是否一致。
description_en: DesignBuddy test-only sample that verifies an installed skill matches its original build.
version: {version}
author: DesignBuddy Dev
user-invocable: true
disable-model-invocation: false
---

# DesignBuddy 安装验证样品（测试专用）

构建标记：`{marker}`
构建编号：`{build_id}`

只做核对，不修改任何文件，不安装任何东西。

## 步骤

1. 原样复述上面的构建标记和构建编号。
2. 读取 @references/rules.md ，原样复述 MUST-COLOR-01 的颜色值。
3. 说明本 Skill 目录的绝对路径，以及你是如何得知的。
4. 用可用的 Python（依次尝试 `python3`、`python`、`py -3`）运行：
   `<python命令> "<Skill目录>/scripts/selfcheck.py"`
   原样贴出 `=== DBPROBE REPORT BEGIN ===` 到 `=== DBPROBE REPORT END ===` 之间的内容。
   如果没有可用的 Python，把这一步记为 BLOCKED。
5. 按下面的格式输出报告：

```
## DBPROBE INSTALL VERIFY REPORT
版本(frontmatter): <...>
构建标记: <...> | 构建编号: <...>
MUST-COLOR-01: <...>
Skill位置: <...> | 获取方式: <...>
selfcheck: <MATCH/MISMATCH/BLOCKED>
<selfcheck 报告原文>
```
"""

RULES_MD = """# Rules

| id | level | rule |
|---|---|---|
| MUST-COLOR-01 | MUST | 主色固定为 `{color}` |
| NEVER-COLOR-02 | NEVER | 使用未在本表中列出的颜色 |

构建标记：`{marker}`
"""

SELFCHECK_PY = r'''#!/usr/bin/env python3
"""Verify that this installed skill matches templates/build-manifest.json."""
import hashlib
import json
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass

root = Path(__file__).resolve().parent.parent
manifest_path = root / "templates" / "build-manifest.json"
print("=== DBPROBE REPORT BEGIN ===")
print("skill_dir: %s" % root)
try:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
except Exception as e:
    print("- [FAIL] manifest unreadable: %s: %s" % (type(e).__name__, e))
    print("=== DBPROBE REPORT END ===")
    sys.exit(1)
print("build_id: %s | version: %s" % (manifest["build_id"], manifest["version"]))
bad = 0
for rel, want in sorted(manifest["files"].items()):
    p = root / rel
    if not p.is_file():
        print("- [MISSING] %s" % rel)
        bad += 1
        continue
    data = p.read_bytes()
    if hashlib.sha256(data).hexdigest() == want:
        print("- [MATCH] %s" % rel)
    elif hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest() == want:
        print("- [MISMATCH-NEWLINE-ONLY] %s (CRLF line endings; content otherwise identical)" % rel)
        bad += 1
    else:
        print("- [MISMATCH] %s" % rel)
        bad += 1
expected = set(manifest["files"]) | {"templates/build-manifest.json"}
for p in sorted(root.rglob("*")):
    if p.is_file():
        rel = p.relative_to(root).as_posix()
        if rel not in expected and "__pycache__" not in rel:
            print("- [EXTRA] %s" % rel)
print("overall: %s" % ("MATCH" if bad == 0 else "MISMATCH"))
print("=== DBPROBE REPORT END ===")
sys.exit(0 if bad == 0 else 1)
'''


def build_files(version, build_id):
    v = VARIANTS[version]
    return {
        "SKILL.md": SKILL_MD.format(name=SKILL_NAME, version=version, marker=v["marker"], build_id=build_id),
        "references/rules.md": RULES_MD.format(color=v["color"], marker=v["marker"]),
        "scripts/selfcheck.py": SELFCHECK_PY,
    }


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:  # noqa: BLE001
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="1.0.0", choices=sorted(VARIANTS))
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    out_root = Path(args.out) if args.out else Path.cwd() / "dbprobe-results" / "generated"
    build_id = "%s-%s" % (_dt.datetime.now().strftime("%Y%m%d%H%M%S"), uuid.uuid4().hex[:6])
    skill_dir = out_root / ("%s-%s" % (SKILL_NAME, args.version)) / SKILL_NAME
    files = build_files(args.version, build_id)

    checks = []
    try:
        if skill_dir.exists():
            for p in sorted(skill_dir.rglob("*"), reverse=True):
                p.unlink() if p.is_file() else p.rmdir()
        hashes = {}
        for rel, text in files.items():
            p = skill_dir / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            data = text.encode("utf-8")
            p.write_bytes(data)  # bytes: identical line endings on every OS
            hashes[rel] = hashlib.sha256(data).hexdigest()
        manifest = {
            "skill": SKILL_NAME, "version": args.version, "build_id": build_id,
            "generated_by": GENERATOR,
            "generated_at": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "files": hashes,
        }
        mp = skill_dir / "templates" / "build-manifest.json"
        mp.parent.mkdir(parents=True, exist_ok=True)
        mp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        checks.append(("PASS", "GEN-WRITE", "Generated skill files from embedded data (no template copy)"))

        zip_path = skill_dir.parent / ("%s-%s.zip" % (SKILL_NAME, args.version))
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for p in sorted(skill_dir.rglob("*")):
                if p.is_file():
                    z.write(p, "%s/%s" % (SKILL_NAME, p.relative_to(skill_dir).as_posix()))
        checks.append(("PASS", "GEN-ZIP", "Packed ZIP with a single top-level skill directory"))
    except Exception as e:  # noqa: BLE001
        checks.append(("FAIL", "GEN-WRITE", "%s: %s" % (type(e).__name__, e)))
        zip_path = None

    print("=== DBPROBE REPORT BEGIN ===")
    print("probe: dbprobe-installation 1.0.0 (generator)")
    print("skill: %s %s" % (SKILL_NAME, args.version))
    print("build_id: %s" % build_id)
    print("rule MUST-COLOR-01: %s" % VARIANTS[args.version]["color"])
    print("skill_dir: %s" % skill_dir)
    print("zip: %s" % zip_path)
    for result, cid, detail in checks:
        print("- [%s] %s — %s" % (result, cid, detail))
    print("=== DBPROBE REPORT END ===")
    return 0 if all(c[0] == "PASS" for c in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
