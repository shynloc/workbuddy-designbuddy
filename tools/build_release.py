#!/usr/bin/env python3
"""Build, verify and package the DesignBuddy QA candidate.

Steps (all local, standard library only):
  1. unit tests
  2. stage designbuddy-qa/ -> build/stage/designbuddy-qa/ and write templates/package-manifest.json
  3. lint the staged skill (WorkBuddy layout, frontmatter, references, paths, secrets, fonts)
  4. pack dist/designbuddy-qa-v<ver>.zip (single top-level dir, fixed timestamps)
  5. compile fixture brands into dist/brand-alpha/ and dist/brand-beta/
  6. extract the ZIP into a path with spaces + CJK, run version/selftest/run-all from the extracted copy
  7. write dist/SHA256SUMS.txt, qa/local-evidence/ and qa/TEST_REPORT_LOCAL.md

Usage: python3 tools/build_release.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "designbuddy-qa"
DIST = ROOT / "dist"
QA_DOCS = ROOT / "qa"
sys.path.insert(0, str(SRC / "scripts"))
sys.dont_write_bytecode = True

import db_package as package, db_qarunner as qarunner, db_util as util  # noqa: E402

VERSION = util.DESIGNBUDDY_VERSION
ZIP_NAME = "designbuddy-qa-v%s.zip" % VERSION
OUT = DIST / ("v%s" % VERSION)          # every version gets its own folder; earlier packages are never touched
EVIDENCE = QA_DOCS / "local-evidence"
EPOCH = "1767225600"  # 2026-01-01T00:00:00Z — pinned generated_at for reproducible fixture outputs


def run(cmd, **kw):
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    env.update(kw.pop("env", {}))
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, **kw)
    return p.returncode, p.stdout, p.stderr


def step(title):
    print("\n== %s" % title)


def main():
    step("1. unit tests")
    code, so, se = run([sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "tests" / "unit")], cwd=str(ROOT))
    print((se or so).strip().splitlines()[-1])
    if code != 0:
        print(se)
        return 1

    step("2. stage + package manifest")
    stage_root = ROOT / "build" / "stage"
    shutil.rmtree(stage_root, ignore_errors=True)
    stage = stage_root / "designbuddy-qa"
    shutil.copytree(SRC, stage, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
    files = {}
    for p in sorted(stage.rglob("*")):
        if p.is_file():
            files[p.relative_to(stage).as_posix()] = util.sha256_bytes(p.read_bytes())
    util.write_json(stage / "templates" / "package-manifest.json",
                    {"skill": util.SKILL_NAME, "version": VERSION, "files": files})
    print("files hashed:", len(files))

    step("3. lint staged skill")
    lint = package.lint_skill(stage)
    print("errors:", lint["errors"], "warnings:", lint["warnings"], "files:", lint["files"], "bytes:", lint["bytes"])
    if lint["errors"]:
        return 1

    step("4. pack QA skill")
    if (DIST / ZIP_NAME).exists():  # v0.1.0 was released at dist/ top level; never overwrite a released version
        print("refusing: %s already released at dist/ — bump the version" % ZIP_NAME)
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    zip_path, zip_sha = package.pack(stage, OUT / ZIP_NAME, "designbuddy-qa")
    fingerprint = util.sha256_file(stage / "templates" / "package-manifest.json")
    (OUT / "PACKAGE_FINGERPRINT.txt").write_text(
        "designbuddy-qa %s\nzip sha256              %s\npackage-manifest sha256 %s\n"
        "报告 environment.json 中的 package.manifest_sha256 应与上面一致。\n" % (VERSION, zip_sha, fingerprint), encoding="utf-8")
    print(zip_path.name, zip_sha, "roots:", package.zip_roots(zip_path))

    step("5. fixture brand packages")
    os.environ["SOURCE_DATE_EPOCH"] = EPOCH
    sums = [(zip_sha, ZIP_NAME)]
    with tempfile.TemporaryDirectory() as t:
        for fixture, folder in (("brand-alpha", "brand-alpha"), ("brand-beta", "brand-beta")):
            res = qarunner.run_fixture(fixture, Path(t) / fixture)
            if not res["ok"]:
                print("fixture failed", fixture, json.dumps(res["build"]["lint"], ensure_ascii=False))
                return 1
            b = res["build"]
            out = OUT / folder
            shutil.rmtree(out, ignore_errors=True)
            out.mkdir(parents=True)
            for key in ("skill_zip", "portable_zip"):
                dst = out / Path(b[key]).name
                shutil.copyfile(b[key], dst)
                sums.append((util.sha256_file(dst), "%s/%s" % (folder, dst.name)))
            shutil.copytree(b["preview_dir"], out / "preview")
            print(folder, b["skill"], b["build_id"], "qa:", b["qa"])
    os.environ.pop("SOURCE_DATE_EPOCH", None)

    step("6. installed-copy verification (extract to a path with spaces + CJK)")
    with tempfile.TemporaryDirectory() as t:
        inst = Path(t) / "WorkBuddy 安装 模拟"
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(inst)
        # Reproduce the OBSERVED WorkBuddy 5.7.7.0 install behaviour: the client adds _user_meta.json.
        (inst / "designbuddy-qa" / "_user_meta.json").write_text('{"simulated": true}', encoding="utf-8")
        entry = inst / "designbuddy-qa" / "scripts" / "designbuddy.py"
        reports = Path(t) / "用户 项目" / "DesignBuddy-QA-Reports"
        c1, v_out, _ = run([sys.executable, str(entry), "version"])
        c2, st_out, _ = run([sys.executable, str(entry), "selftest"])
        c3, ra_out, ra_err = run([sys.executable, str(entry), "run-all", "--out", str(reports)], cwd=str(Path(t)))
        print("version exit", c1, "selftest exit", c2, json.loads(st_out).get("ok"), "run-all exit", c3)
        if c3 != 0:
            print(ra_out, ra_err)
            return 1
        ra = json.loads(ra_out)
        rdir = Path(ra["report_dir"])
        ev = EVIDENCE
        shutil.rmtree(ev, ignore_errors=True)
        ev.mkdir(parents=True)
        for n in ("TEST_REPORT.md", "results.json", "environment.json", "issues.md", "artifacts-manifest.json", "next-session-prompts.md"):
            shutil.copyfile(rdir / n, ev / n)
        write_local_report(ra, json.loads(v_out), json.loads(st_out), lint, zip_sha, fingerprint)
        write_test_matrix()

    step("7. checksums")
    (OUT / "SHA256SUMS.txt").write_text("".join("%s  %s\n" % s for s in sums), encoding="utf-8")
    print((OUT / "SHA256SUMS.txt").read_text(encoding="utf-8"))
    shutil.rmtree(ROOT / "build", ignore_errors=True)
    return 0


def write_test_matrix():
    res = json.loads((QA_DOCS / "local-evidence" / "results.json").read_text(encoding="utf-8"))
    areas = {"ENV": "运行环境", "PKG": "包装与资源", "CORE": "核心功能", "QA": "设计质量", "SEC": "安全与隐私",
             "INS": "安装链路", "MB": "多品牌", "PP": "付费加密", "UX": "用户体验"}
    L = ["# TEST_MATRIX — DesignBuddy QA v%s" % VERSION, "",
         "由 `tools/build_release.py` 从 QA Runner 的用例定义自动生成。Test ID 稳定，后续版本只新增、不重排。", "",
         "执行类型：**SCRIPT** = QA Runner 自动判定；**AGENT** = WorkBuddy 中的 Agent 按协议执行并用 `record` 回填；"
         "**MANUAL** = 需要用户操作或独立新会话。", ""]
    for code, title in areas.items():
        rows = [c for c in res["cases"] if c["area"] == code]
        L += ["## %s · %s（%d）" % (code, title, len(rows)), "", "| ID | 类型 | 级别 | 目标 | 预期 | 开发机结果 |", "|---|---|---|---|---|---|"]
        L += ["| %s | %s | %s | %s | %s | %s |" % (c["id"], c["execution_type"], c["severity"], c["objective"].replace("|", "/"),
                                              c["expected"].replace("|", "/"), c["result"]) for c in rows]
        L.append("")
    counts = {}
    for c in res["cases"]:
        counts[c["execution_type"]] = counts.get(c["execution_type"], 0) + 1
    L += ["合计 %d 个用例：%s。" % (len(res["cases"]), "、".join("%s %d" % kv for kv in sorted(counts.items()))), ""]
    (QA_DOCS / "TEST_MATRIX.md").write_text("\n".join(L), encoding="utf-8")


def write_local_report(ra, ver, selftest, lint, zip_sha, fingerprint):
    res = json.loads((QA_DOCS / "local-evidence" / "results.json").read_text(encoding="utf-8"))
    env = json.loads((QA_DOCS / "local-evidence" / "environment.json").read_text(encoding="utf-8"))
    s = res["summary"]
    L = ["# TEST_REPORT_LOCAL — DesignBuddy QA v%s" % VERSION, "",
         "开发机本地测试证据。由 `tools/build_release.py` 自动生成，**不代表 WorkBuddy 真机结果**。", "",
         "## 测试环境", "",
         "- 平台：%s（%s）" % (env["platform"], env["machine"]),
         "- Python：%s；PATH 中的 node：%s" % (env["python"]["version"], env["tools_on_path"]["node"]),
         "- 运行方式：把 `dist/v%s/%s` 解压到含空格和中文的路径，并写入模拟的平台元数据 `_user_meta.json`（复现 WorkBuddy 5.7.7.0 的安装行为），然后从解压后的副本执行" % (VERSION, ZIP_NAME),
         "- 安装包：zip sha256 `%s`；package-manifest sha256 `%s`" % (zip_sha, fingerprint),
         "- WorkBuddy：**未参与**（开发容器中没有 WorkBuddy 客户端）", "",
         "## 结果", "",
         "| 项 | 结果 |", "|---|---|",
         "| 单元测试（tests/unit） | 通过 |",
         "| Skill lint（结构 / frontmatter / 引用 / 路径 / 密钥 / 字体） | errors=%d warnings=%d，%d 个文件，%d bytes |" % (len(lint["errors"]), len(lint["warnings"]), lint["files"], lint["bytes"]),
         "| `version` | %s %s |" % (ver["name"], ver["version"]),
         "| `selftest`（package-manifest 完整性） | ok=%s，%s 个文件 |" % (selftest["ok"], selftest.get("files")),
         "| QA RUN ALL 用例 | %d 个 |" % s["total"],
         "| PASS / FAIL / PARTIAL / BLOCKED / NOT_TESTED | %s |" % " / ".join(str(s["counts"][k]) for k in qarunner.RESULTS),
         "| SCRIPT 通过率 | %s%%（%d/%d） |" % (s["script_pass_rate"], s["script_pass"], s["script_total"]),
         "| 问题 P0/P1/P2/P3 | %s |" % " / ".join(str(s["issues"][k]) for k in ("P0", "P1", "P2", "P3")), "",
         "## 未验证项（需要 WorkBuddy 真机或人工）", ""]
    for c in res["cases"]:
        if c["result"] in ("BLOCKED", "NOT_TESTED"):
            L.append("- `%s` %s · %s — %s" % (c["id"], c["result"], c["objective"], c["error_or_block_reason"]))
    L += ["", "## 状态", ""] + ["- %s：%s" % kv for kv in s["states"].items()]
    L += ["", "> LOCAL_QA_PASSED 为 NO 是预期结果：ENV-007/008/009、INS-*、MB-003..005 必须在 WorkBuddy 中执行并回填。", "",
          "完整原始输出见 `qa/local-evidence/`（TEST_REPORT.md、results.json 等）。上一版本的证据见 `qa/history/`。", ""]
    (QA_DOCS / "TEST_REPORT_LOCAL.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
