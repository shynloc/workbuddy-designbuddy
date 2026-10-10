#!/usr/bin/env python3
"""Build the clean commercial package dist/v<ver>/designbuddy-v<ver>.zip.

Derived from the same source as the QA build, minus everything QA-only:
QA runner, QA protocol, fixture brands and malformed inputs. The compiler,
templates, runtime self-check (selftest) and delivery are kept unchanged.

Verification (all local, standard library only):
  unit tests -> stage + strip -> forbidden-content scan -> package manifest
  -> lint -> pack -> extract to a path with spaces + CJK (+ simulated
  _user_meta.json) -> version / selftest / env / unavailable QA commands
  -> two end-to-end brand builds through the CLI (existing + new path)
  -> deliver to a temporary Downloads folder -> lint + selfcheck the
  delivered Brand Skill ZIP -> checksums + BUILD_VERIFICATION.md

This script never uploads or publishes anything.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "designbuddy-qa"
COMMERCIAL = ROOT / "release" / "commercial"
FIX = SRC / "templates" / "fixtures"
sys.path.insert(0, str(SRC / "scripts"))
sys.dont_write_bytecode = True

from dbcore import package, util  # noqa: E402

VERSION = "1.0.0"
NAME = "designbuddy"
OUT = ROOT / "dist" / ("v%s" % VERSION)
ZIP_NAME = "%s-v%s.zip" % (NAME, VERSION)
REMOVE = ["templates/fixtures", "scripts/dbcore/qarunner.py", "references/qa-protocol.md"]
FORBIDDEN = [r"qa-protocol", r"qarunner", r"templates/fixtures", r"Alpha Demo", r"Beta Demo", r"Gamma Demo",
             r"测试候选版", r"QA RUN ALL", r"designbuddy-qa"]


def run(cmd, env_extra=None, cwd=None):
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    env.update(env_extra or {})
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, cwd=cwd)
    data = None
    if p.stdout.strip().startswith("{"):
        data = json.loads(p.stdout)
    return p.returncode, data, p.stderr


def stage():
    root = ROOT / "build" / "commercial"
    shutil.rmtree(root, ignore_errors=True)
    st = root / NAME
    shutil.copytree(SRC, st, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store", "package-manifest.json"))
    for rel in REMOVE:
        t = st / rel
        shutil.rmtree(t) if t.is_dir() else t.unlink()
    shutil.copyfile(COMMERCIAL / "SKILL.md", st / "SKILL.md")
    u = st / "scripts" / "dbcore" / "util.py"
    s = u.read_text(encoding="utf-8")
    s = s.replace('DESIGNBUDDY_VERSION = "%s"' % util.DESIGNBUDDY_VERSION, 'DESIGNBUDDY_VERSION = "%s"' % VERSION)
    s = s.replace('SKILL_NAME = "designbuddy-qa"', 'SKILL_NAME = "%s"' % NAME)
    u.write_text(s, encoding="utf-8")
    init = st / "scripts" / "dbcore" / "__init__.py"
    init.write_text('"""DesignBuddy core. Standard library only."""\n', encoding="utf-8")
    cli = st / "scripts" / "designbuddy.py"
    lines = [l for l in cli.read_text(encoding="utf-8").splitlines(True)
             if not re.match(r"^  (fixture|run-all|record|finalize)\s", l)]
    cli.write_text("".join(lines).replace("DesignBuddy QA command-line entry point.", "DesignBuddy command-line entry point."), encoding="utf-8")
    cc = st / "references" / "compiler-contract.md"
    cc.write_text("".join(l for l in cc.read_text(encoding="utf-8").splitlines(True)
                          if not l.startswith(("| `run-all", "| `record"))), encoding="utf-8")
    dl = st / "scripts" / "dbcore" / "deliver.py"
    dl.write_text(dl.read_text(encoding="utf-8").replace("QA helper: copy", "Copy"), encoding="utf-8")
    return st


def scan_forbidden(st):
    hits = []
    for p in st.rglob("*"):
        if p.is_file() and p.suffix in (".md", ".py", ".json", ".tmpl", ".txt", ".html", ".css"):
            t = p.read_text(encoding="utf-8", errors="replace")
            for pat in FORBIDDEN:
                # designbuddy.py keeps a guarded lazy import (returns E_UNAVAILABLE when qarunner is absent; verified below)
                if pat == r"qarunner" and p.name == "designbuddy.py":
                    continue
                if re.search(pat, t):
                    hits.append("%s: %s" % (p.relative_to(st).as_posix(), pat))
    return hits


def e2e(entry, tmp, label, brief, steps):
    ws = tmp / ("工作区 %s" % label)
    dl = tmp / "Downloads 下载"
    dl.mkdir(exist_ok=True)
    env = {"DESIGNBUDDY_DOWNLOADS": str(dl)}
    log = []
    code, d, _ = run([sys.executable, str(entry), "init", "--brief", str(brief), "--workspace", str(ws)], env)
    log.append(("init", code))
    for st in steps:
        if st == "preview":
            code, d, _ = run([sys.executable, str(entry), "preview", "--workspace", str(ws)], env)
        else:
            g, dec, *sets = st
            cmd = [sys.executable, str(entry), "gate", "--workspace", str(ws), "--gate", g, "--decision", dec]
            for kv in sets:
                cmd += ["--set", kv]
            code, d, _ = run(cmd, env)
        log.append((st if isinstance(st, str) else " ".join(st), code))
    code, b, err = run([sys.executable, str(entry), "build", "--workspace", str(ws), "--deliver"], env)
    log.append(("build --deliver", code))
    ok_steps = all(c == 0 for _, c in log)
    delivered = b.get("delivery", {}) if b else {}
    zip_path = Path(delivered.get("skill_zip", "")) if delivered.get("ok") else None
    lint_ok, selfcheck = False, None
    if zip_path and zip_path.is_file():
        x = tmp / ("解压 %s" % label)
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(x)
        sk = x / package.zip_roots(zip_path)[0]
        lint_ok = not package.lint_skill(sk)["errors"]
        c, _, _ = run([sys.executable, str(sk / "scripts" / "selfcheck.py")])
        p = subprocess.run([sys.executable, str(sk / "scripts" / "selfcheck.py")], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        selfcheck = "MATCH" if "overall: MATCH" in p.stdout and p.returncode == 0 else p.stdout[-200:]
    return {"label": label, "steps_ok": ok_steps, "log": log, "qa": (b or {}).get("qa"), "delivered_to_downloads": bool(zip_path),
            "files_delivered": len(delivered.get("files", [])), "brand_skill_lint_ok": lint_ok, "brand_skill_selfcheck": selfcheck,
            "build_id": (b or {}).get("build_id")}


def main():
    print("== unit tests")
    code, _, err = run([sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "tests" / "unit")], cwd=str(ROOT))
    print(err.strip().splitlines()[-1])
    if code:
        return 1

    print("== stage + strip QA-only content")
    st = stage()
    hits = scan_forbidden(st)
    print("forbidden content:", hits or "none")
    if hits:
        return 1

    files = {p.relative_to(st).as_posix(): util.sha256_bytes(p.read_bytes()) for p in sorted(st.rglob("*")) if p.is_file()}
    util.write_json(st / "templates" / "package-manifest.json", {"skill": NAME, "version": VERSION, "files": files})
    lint = package.lint_skill(st)
    print("lint:", lint["errors"] or "0 errors", "files:", lint["files"], "bytes:", lint["bytes"])
    if lint["errors"]:
        return 1

    print("== pack")
    OUT.mkdir(parents=True, exist_ok=True)
    zip_path, zip_sha = package.pack(st, OUT / ZIP_NAME, NAME)
    fingerprint = util.sha256_file(st / "templates" / "package-manifest.json")
    print(ZIP_NAME, zip_sha, package.zip_roots(zip_path))

    print("== verify extracted copy")
    results = {}
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        inst = tmp / "WorkBuddy skills 模拟"
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(inst)
        (inst / NAME / "_user_meta.json").write_text("{}", encoding="utf-8")  # OBSERVED platform behaviour
        entry = inst / NAME / "scripts" / "designbuddy.py"
        c, v, _ = run([sys.executable, str(entry), "version"])
        results["version"] = (c, v)
        c, s, _ = run([sys.executable, str(entry), "selftest"])
        results["selftest"] = (c, s)
        c, e, _ = run([sys.executable, str(entry), "env"], {"DESIGNBUDDY_DOWNLOADS": str(tmp)})
        results["env"] = (c, (e or {}).get("environment", {}).get("package"))
        c, q, _ = run([sys.executable, str(entry), "run-all", "--out", str(tmp / "x")])
        results["qa_unavailable"] = (c, (q or {}).get("error", {}).get("code"))
        results["existing"] = e2e(entry, tmp, "existing", FIX / "brand-alpha.json",
                                  [("G1", "KEEP"), ("G2", "KEEP"), ("G3", "CHANGE", "resolve.conflict-colors-primary=#1F4FD8"),
                                   ("G3", "KEEP"), ("G4", "KEEP"), "preview", ("G5", "KEEP"), ("G6", "KEEP")])
        results["new"] = e2e(entry, tmp, "new", FIX / "brand-gamma-new.json",
                             [("G1", "KEEP"), ("G2", "KEEP", "direction=bold-technical"), ("G3", "KEEP"), ("G4", "KEEP"),
                              "preview", ("G5", "KEEP"), ("G6", "KEEP")])
    checks = {
        "version": results["version"][0] == 0 and results["version"][1]["version"] == VERSION and results["version"][1]["name"] == NAME,
        "selftest": results["selftest"][0] == 0 and results["selftest"][1]["ok"]
        and results["selftest"][1]["installed_extras"] == {"platform": ["_user_meta.json"], "unknown": []},
        "env_fingerprint": results["env"][0] == 0 and results["env"][1]["manifest_sha256"] == fingerprint,
        "qa_commands_unavailable": results["qa_unavailable"] == (2, "E_UNAVAILABLE"),
    }
    for k in ("existing", "new"):
        r = results[k]
        checks["e2e_" + k] = r["steps_ok"] and r["delivered_to_downloads"] and r["brand_skill_lint_ok"] and r["brand_skill_selfcheck"] == "MATCH" \
            and r["qa"]["passed"]
    for k, v in checks.items():
        print("[%s] %s" % ("PASS" if v else "FAIL", k))
    if not all(checks.values()):
        print(json.dumps(results, ensure_ascii=False, indent=1, default=str))
        return 1

    (OUT / "SHA256SUMS.txt").write_text("%s  %s\n" % (zip_sha, ZIP_NAME), encoding="utf-8")
    (OUT / "PACKAGE_FINGERPRINT.txt").write_text(
        "%s %s\nzip sha256              %s\npackage-manifest sha256 %s\n" % (NAME, VERSION, zip_sha, fingerprint), encoding="utf-8")
    L = ["# BUILD_VERIFICATION — %s v%s" % (NAME, VERSION), "",
         "由 `tools/build_commercial.py` 自动生成，是开发机上的本地验证证据，**不代表平台解析、审核或付费加密环境中的结果**。", "",
         "- ZIP：`%s`" % ZIP_NAME, "- ZIP SHA-256：`%s`" % zip_sha, "- package-manifest SHA-256：`%s`" % fingerprint,
         "- 根目录：`%s/`；%d 个文件；%d bytes；lint 0 错误" % (NAME, lint["files"], lint["bytes"]),
         "- 已剔除 QA 专用内容：%s；对 %d 个禁用词的扫描结果：无命中" % (", ".join(REMOVE), len(FORBIDDEN)), "",
         "| 检查 | 结果 |", "|---|---|"]
    L += ["| %s | %s |" % (k, "PASS" if v else "FAIL") for k, v in checks.items()]
    L += ["", "## 端到端（从解压后的商业包运行 CLI，交付到临时的下载文件夹）", ""]
    for k in ("existing", "new"):
        r = results[k]
        L.append("- **%s**：步骤 %s；Brand QA %s；交付文件 %d 个；交付的 Brand Skill 通过 lint=%s，selfcheck=%s；build_id `%s`" % (
            k, " → ".join("%s(%d)" % s for s in r["log"]), r["qa"], r["files_delivered"], r["brand_skill_lint_ok"],
            r["brand_skill_selfcheck"], r["build_id"]))
    (OUT / "BUILD_VERIFICATION.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    shutil.rmtree(ROOT / "build", ignore_errors=True)
    print("ok ->", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
