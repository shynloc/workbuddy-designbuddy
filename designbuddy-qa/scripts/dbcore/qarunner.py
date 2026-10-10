"""QA RUN ALL — deterministic acceptance test runner.

Executes real commands, writes real files, checks real return codes. Tests
that need the WorkBuddy platform or a human are emitted as AGENT / MANUAL
cases with result NOT_TESTED or BLOCKED; they are never marked PASS here.
"""
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

from . import color as C, engine, exporters, ir as IR, package, qa, workspace as W
from .util import (DBError, DESIGNBUDDY_VERSION, SCHEMA_VERSION, SKILL_NAME, SKILL_ROOT, TEMPLATES,
                   dump_json, leaks, now_iso, read_json, redact, redact_obj, sha256_bytes, write_json, write_text)

RESULTS = ("PASS", "FAIL", "PARTIAL", "BLOCKED", "NOT_TESTED")
FIXTURES = TEMPLATES / "fixtures"
MALFORMED = FIXTURES / "malformed-inputs"
ENTRY = SKILL_ROOT / "scripts" / "designbuddy.py"
PP_BLOCK = "BLOCKED: REQUIRES_PAID_ENCRYPTED_MARKETPLACE_RUNTIME"
# Files the WorkBuddy client adds to an installed skill root. OBSERVED: WorkBuddy 5.7.7.0 / Windows 11
# writes `_user_meta.json` at install time. Only the file NAME is checked; its content is never read.
PLATFORM_META = {"_user_meta.json"}
INS_IDS = ("INS-001", "INS-002", "INS-003", "INS-004", "INS-005")


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


# ---------------------------------------------------------------- fixtures

def run_fixture(name, ws, steps=None):
    """Run a fixture brief end to end through the real gate engine."""
    brief_path = FIXTURES / ("%s.json" % name)
    if not brief_path.is_file():
        raise DBError("E_FIXTURE", "未知夹具：%s" % name)
    brief = read_json(brief_path)
    t0 = time.time()
    log = [{"step": "init", "result": W.init(brief_path, ws, force=True)["gates"]}]
    for d in steps or brief.get("fixture_decisions", []):
        if d.get("step") == "preview":
            res = W.preview(ws)
            log.append({"step": "preview", "qa": res["qa"]})
        else:
            res = W.gate(ws, d["gate"], d["decision"], d.get("patch"))
            log.append({"step": "%s %s" % (d["gate"], d["decision"]), "gates": res["gates"]})
    build = W.build(ws, force=True)
    return {"ok": build["ok"], "fixture": name, "seconds": round(time.time() - t0, 2), "log": log, "build": build,
            "decisions": len([d for d in brief.get("fixture_decisions", []) if "gate" in d])}


# ---------------------------------------------------------------- runner

class Runner:
    def __init__(self, out_dir):
        self.out = Path(out_dir)
        self.art = self.out / "artifacts"
        self.work = self.out / ".qa-work"  # deleted at the end of the run; never part of artifacts
        self.art.mkdir(parents=True, exist_ok=True)
        self.cases = []
        self.env = environment()
        self.ctx = "SCRIPT · %s · Python %s · 安装形态见 ENV-008" % (sys.platform, platform.python_version())
        self.fixtures = {}

    def case(self, cid, area, objective, expected, severity, fn, execution_type="SCRIPT"):
        rec = {"id": cid, "area": area, "objective": objective, "expected": expected, "actual": "",
               "result": "NOT_TESTED", "execution_type": execution_type, "runtime_context": self.ctx,
               "steps": [], "commands_or_actions": [], "artifact_paths": [], "evidence": "",
               "error_or_block_reason": "", "severity": severity, "suggested_fix": ""}
        t0 = time.time()
        try:
            r = fn() or {}
            rec.update({k: r[k] for k in r if k in rec})
        except DBError as e:
            rec.update(result="FAIL", actual="DBError %s: %s" % (e.code, e.message), error_or_block_reason=e.code)
        except Exception as e:  # noqa: BLE001 - a crashing test must still be reported
            rec.update(result="FAIL", actual="%s: %s" % (type(e).__name__, e), error_or_block_reason="TEST_CRASHED")
        rec["seconds"] = round(time.time() - t0, 3)
        if rec["result"] not in RESULTS:
            rec["result"] = "FAIL"
        self.cases.append(rec)
        return rec

    def pending(self, cid, area, objective, expected, severity, execution_type, result, reason, steps):
        rec = {"id": cid, "area": area, "objective": objective, "expected": expected, "actual": "",
               "result": result, "execution_type": execution_type, "runtime_context": "需要在 WorkBuddy 中由 Agent/用户执行",
               "steps": steps, "commands_or_actions": [], "artifact_paths": [], "evidence": "",
               "error_or_block_reason": reason, "severity": severity, "suggested_fix": "", "seconds": 0}
        self.cases.append(rec)

    def rel(self, p):
        try:
            return Path(p).resolve().relative_to(self.out.resolve()).as_posix()
        except ValueError:
            return redact(str(p), {"<SKILL>": str(SKILL_ROOT)})

    def sub(self, *args):
        cmd = [sys.executable, str(ENTRY)] + [str(a) for a in args]
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120, env=_child_env())
        shown = "python designbuddy.py " + " ".join(self.rel(a) if os.sep in str(a) else str(a) for a in args)
        return p.returncode, p.stdout, p.stderr, shown


def ok(cond, actual, evidence="", paths=None, cmds=None, fix="", partial=False):
    return {"result": "PASS" if cond else ("PARTIAL" if partial else "FAIL"), "actual": actual, "evidence": evidence,
            "artifact_paths": paths or [], "commands_or_actions": cmds or [], "suggested_fix": "" if cond else fix}


def expect_error(fn, code):
    try:
        fn()
    except DBError as e:
        return e.code == code, "DBError %s: %s" % (e.code, e.message)
    return False, "未报错（期望 %s）" % code


def run_all(out=None):
    run_id = "qa-%s-%s" % (time.strftime("%Y%m%d-%H%M%S"), uuid.uuid4().hex[:4])
    out_dir = Path(out) if out else Path.cwd() / "DesignBuddy-QA-Reports" / run_id
    if out and out_dir.exists() and any(out_dir.iterdir()):
        out_dir = out_dir / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    R = Runner(out_dir)
    R.run_id = run_id
    write_json(out_dir / "results.json", {"run_id": run_id, "status": "RUNNING", "cases": []})
    try:
        _env_tests(R)
        _pkg_tests(R)
        _core_tests(R)
        _qa_tests(R)
        _sec_tests(R)
        _ins_tests(R)
        _mb_tests(R)
        _pp_tests(R)
        _ux_tests(R)
    finally:
        shutil.rmtree(R.work, ignore_errors=True)
        write_reports(R.out, run_id, R.cases, R.env)
        _post_redaction_check(R)
        write_reports(R.out, run_id, R.cases, R.env)
    s = summarize(R.cases)
    return {"ok": True, "run_id": run_id, "report_dir": str(out_dir), "summary": s,
            "report": str(out_dir / "TEST_REPORT.md"), "results": str(out_dir / "results.json")}


# ---------------------------------------------------------------- ENV

def _env_tests(R):
    e = R.env
    R.case("ENV-001", "ENV", "Skill 脚本能在当前环境用 Python 运行", "Python ≥ 3.8 正常执行", "P0",
           lambda: ok(sys.version_info >= (3, 8), "Python %s (%s)" % (e["python"]["version"], e["python"]["implementation"]),
                      "sys.version_info=%s" % (tuple(sys.version_info[:3]),)))
    R.case("ENV-002", "ENV", "记录操作系统与 shell 线索", "得到 OS 与 shell 信息", "P2",
           lambda: ok(True, "%s · shell 线索 %s" % (e["platform"], {k: v for k, v in e["shell_hints"].items() if v}),
                      "macOS 与 Windows 结果互不替代"))

    def writable():
        d = R.work / "中文 目录 test"
        d.mkdir(parents=True, exist_ok=True)
        f = d / "写入 测试.json"
        f.write_text('{"ok": "✓"}', encoding="utf-8")
        good = json.loads(f.read_text(encoding="utf-8")) == {"ok": "✓"}
        f.unlink()
        return ok(good, "报告目录可写，含中文与空格路径的读写往返成功", paths=[R.rel(R.out)])
    R.case("ENV-003", "ENV", "报告目录可写（含中文/空格路径）", "写入、读取、删除成功", "P0", writable)

    def cwd():
        try:
            p = Path.cwd() / (".designbuddy-write-test-%s" % uuid.uuid4().hex[:6])
            p.write_text("x", encoding="utf-8")
            p.unlink()
            return ok(True, "当前工作目录可写")
        except OSError as ex:
            return {"result": "PARTIAL", "actual": "当前工作目录不可写：%s" % type(ex).__name__,
                    "suggested_fix": "让用户指定一个可写的项目文件夹作为输出目录"}
    R.case("ENV-004", "ENV", "当前工作目录可写性", "可写；不可写时需改用用户指定目录", "P2", cwd)
    R.case("ENV-005", "ENV", "Node 可用性探测（仅记录）", "完成探测", "P3",
           lambda: ok(True, "node 在 PATH 中：%s（v0.1 不依赖 Node）" % e["tools_on_path"]["node"]))
    for cid, obj, sev in (("ENV-007", "记录 WorkBuddy 客户端版本", "P2"),
                          ("ENV-008", "记录 Skill 安装形态：本地/市场、是否付费、是否加密、开发者/购买者", "P1"),
                          ("ENV-009", "记录 Agent 实际使用的 shell 与命令执行方式", "P2")):
        R.pending(cid, "ENV", obj, "Agent 如实记录", sev, "AGENT", "NOT_TESTED", "需要 Agent 在 WorkBuddy 中记录",
                  ["按 references/qa-protocol.md 的 ENV 部分执行，然后用 record 命令写入"])


# ---------------------------------------------------------------- PKG

def _pkg_tests(R):
    lint = package.lint_skill(SKILL_ROOT, platform_files=PLATFORM_META)
    R.case("PKG-001", "PKG", "SKILL.md frontmatter 合法且必填字段齐全", "无 frontmatter 错误", "P0",
           lambda: ok(lint["frontmatter"] and not [x for x in lint["errors"] if "frontmatter" in x or "version" in x or "name" in x],
                      "name=%s version=%s" % ((lint["frontmatter"] or {}).get("name"), (lint["frontmatter"] or {}).get("version")),
                      json.dumps([x for x in lint["errors"] if "frontmatter" in x], ensure_ascii=False)))
    R.case("PKG-002", "PKG", "所有 @references 引用都能解析", "无缺失引用", "P0",
           lambda: ok(not [x for x in lint["errors"] if "引用" in x or "@references" in x], "检查 SKILL.md 中的引用",
                      json.dumps([x for x in lint["errors"] if "引用" in x or "@references" in x], ensure_ascii=False)))
    need = ["scripts/designbuddy.py", "scripts/dbcore/engine.py", "scripts/dbcore/exporters.py", "scripts/dbcore/qarunner.py",
            "templates/brand-skill/SKILL.md.tmpl", "templates/preview/poster.html.tmpl", "templates/portable/DESIGN.md.tmpl",
            "templates/data/directions.json", "templates/data/fonts.json", "templates/fixtures/brand-alpha.json",
            "templates/fixtures/brand-beta.json", "templates/fixtures/brand-gamma-new.json", "references/qa-protocol.md",
            "references/installation-handoff.md", "references/design-workflow.md", "references/compiler-contract.md", "references/safety.md"]
    R.case("PKG-003", "PKG", "必需脚本、模板、夹具存在", "全部存在", "P0",
           lambda: ok(all((SKILL_ROOT / n).is_file() for n in need), "缺失：%s" % ([n for n in need if not (SKILL_ROOT / n).is_file()] or "无")))

    def integ():
        res = package_integrity()
        if "reason" in res:
            return {"result": "NOT_TESTED", "actual": res["reason"], "error_or_block_reason": "仅在打包后的 Skill 中可测"}
        return ok(res["ok"], "检查 %d 个文件；不一致 %s；缺失 %s" % (res["files"], res["mismatch"] or "无", res["missing"] or "无"),
                  fix="重新安装 designbuddy-qa ZIP；若仍不一致，说明安装过程改写了文件")
    R.case("PKG-004", "PKG", "安装后的包与发布构建一致（package-manifest）", "全部 SHA-256 一致", "P1", integ)
    R.case("PKG-005", "PKG", "包内无绝对路径、密钥、字体、垃圾文件、非标准根目录项", "lint 无错误", "P0",
           lambda: ok(not lint["errors"], "lint errors=%d warnings=%d files=%d；平台元数据（另见 PKG-008）：%s" % (
                          len(lint["errors"]), len(lint["warnings"]), lint["files"], lint.get("platform_files") or "无"),
                      json.dumps(lint["errors"][:10], ensure_ascii=False)))

    def entry():
        code, so, se, shown = R.sub("version")
        data = json.loads(so) if so.strip().startswith("{") else {}
        return ok(code == 0 and data.get("version") == DESIGNBUDDY_VERSION, "exit=%d version=%s" % (code, data.get("version")),
                  cmds=[shown], evidence=(se or "")[:200])
    R.case("PKG-006", "PKG", "入口脚本可作为独立子进程执行", "退出码 0，版本号正确", "P0", entry)

    def extras():
        ex = installed_extras()
        if ex is None:
            return {"result": "NOT_TESTED", "actual": "开发源码未经打包，没有 package-manifest", "error_or_block_reason": "仅在打包后的 Skill 中可测"}
        return ok(not ex["unknown"], "平台元数据文件：%s；未知额外文件：%s" % (ex["platform"] or "无", ex["unknown"] or "无"),
                  "平台元数据只核对文件名，不读取内容（隐私）。已知列表：%s" % sorted(PLATFORM_META),
                  fix="未知额外文件可能来自安装过程或他人改动，请检查后重新安装")
    R.case("PKG-008", "PKG", "安装副本中的额外文件：平台元数据与未知文件分开判定", "没有未知的额外文件", "P1", extras)

    def tmpl():
        names = ["brand-skill/SKILL.md.tmpl", "preview/poster.html.tmpl", "preview/onepager.html.tmpl", "portable/DESIGN.md.tmpl"]
        sizes = {n: len((TEMPLATES / n).read_text(encoding="utf-8")) for n in names}
        return ok(all(sizes.values()), "运行时读取模板成功：%s" % sizes)
    R.case("PKG-007", "PKG", "运行时可读取内置模板", "模板可读且非空", "P0", tmpl)


# ---------------------------------------------------------------- CORE

def _fx(R, name):
    if name not in R.fixtures:
        ws = R.work / name
        R.fixtures[name] = run_fixture(name, ws)
        R.fixtures[name]["ws"] = ws
    return R.fixtures[name]


def _core_tests(R):
    def existing():
        brief = read_json(FIXTURES / "brand-alpha.json")
        ir0 = engine.intake(brief)
        conflict = [c for c in ir0["conflicts"] if c["field"] == "colors.primary"]
        res = _fx(R, "brand-alpha")
        ir1, _ = W.load(res["ws"])
        resolved = all(c["status"] == "resolved" for c in ir1["conflicts"])
        rep = IR.validate(ir1, "release")
        return ok(bool(conflict) and resolved and not rep["errors"] and res["ok"],
                  "检测到冲突 %d 个，已裁决=%s，release 校验错误 %d，构建 ok=%s" % (len(conflict), resolved, len(rep["errors"]), res["ok"]),
                  "primary 候选：%s" % [c["value"] for c in conflict[0]["candidates"]] if conflict else "",
                  [R.rel(res["ws"] / "brand-ir/brand-ir.json")], ["fixture brand-alpha（Existing）"])
    R.case("CORE-001", "CORE", "Existing 路径：导入→冲突检测→裁决→Brand IR", "冲突被检测并经 Gate 裁决，IR 通过 release 校验", "P0", existing)

    def partial():
        res = _fx(R, "brand-beta")
        ir1, _ = W.load(res["ws"])
        prim = next(c for c in ir1["design_system"]["colors"] if c["role"] == "primary")["hex"]
        gen = [c["role"] for c in ir1["design_system"]["colors"] if c["hex"]["source_type"] == "GENERATED"]
        head = ir1["design_system"]["typography"]["families"][0]["family"]
        good = prim["value"] == "#9A3412" and prim["source_type"] == "USER_CONFIRMED" and "ink" in gen and head["source_type"] == "GENERATED" and res["ok"]
        return ok(good, "主色保留 %s(%s)；生成角色 %s；标题字体 %s(%s)" % (prim["value"], prim["source_type"], gen, head["value"], head["source_type"]),
                  paths=[R.rel(res["ws"] / "brand-ir/brand-ir.json")])
    R.case("CORE-002", "CORE", "Partial 路径：保留已知规则，补全缺口", "已知主色保留；缺失项标记 GENERATED", "P0", partial)

    def new():
        brief = read_json(FIXTURES / "brand-gamma-new.json")
        ir0 = engine.intake(brief)
        res = _fx(R, "brand-gamma-new")
        ir1, _ = W.load(res["ws"])
        good = ir0["design_system"] is None and len(ir0["candidates"]) == 3 and ir1["design_system"]["direction"]["id"] == "bold-technical" and res["ok"]
        return ok(good, "候选方向 %s → 选择 %s" % ([c["id"] for c in ir0["candidates"]], ir1["design_system"]["direction"]["id"]),
                  paths=[R.rel(res["ws"] / "brand-ir/brand-ir.json")])
    R.case("CORE-003", "CORE", "New 路径：Discovery→2–3 个方向→选择→完整系统", "生成 3 个候选，选择后得到完整系统", "P0", new)

    def schema():
        good, msg = expect_error(lambda: W.load(_copy_ir_with(R, {"schema_version": "9.9.9"})), "E_SCHEMA_VERSION")
        rep = IR.validate(read_json(MALFORMED / "wrong-schema-ir.json"))
        return ok(good and any(e["code"] == "E_SCHEMA_VERSION" for e in rep["errors"]), msg)
    R.case("CORE-004", "CORE", "schema_version 校验", "错误版本被拒绝", "P1", schema)

    def prov():
        ir1, _ = W.load(_fx(R, "brand-alpha")["ws"])
        facts = list(IR.iter_facts(ir1))
        bad = [p for p, f in facts if f["source_type"] not in IR.SOURCE_TYPES or f["confidence"] not in IR.CONFIDENCE]
        counts = engine.provenance_summary(ir1)["counts"]
        return ok(facts and not bad and len(counts) >= 3, "%d 个事实；分布 %s" % (len(facts), counts))
    R.case("CORE-005", "CORE", "Provenance / Confidence 覆盖", "每个事实都有合法来源与置信度", "P1", prov)

    def gates():
        ws = R.work / "gate-order"
        W.init(FIXTURES / "brand-beta.json", ws, force=True)
        a, m1 = expect_error(lambda: W.gate(ws, "G3", "KEEP"), "E_GATE_ORDER")
        b, m2 = expect_error(lambda: W.build(ws), "E_NOT_READY")
        c, m3 = expect_error(lambda: W.gate(ws, "G1", "CHANGE", {"color.primary": "#000000"}), "E_PATCH")
        return ok(a and b and c, "跳过 G1 直接 G3：%s；未过 Gate 构建：%s；越权修改：%s" % (m1, m2, m3))
    R.case("CORE-006", "CORE", "Design Gates 顺序与放行", "跳级、未确认构建、越权修改都被拒绝", "P0", gates)

    def skill():
        b = _fx(R, "brand-alpha")["build"]
        roots = package.zip_roots(b["skill_zip"])
        return ok(not b["lint"]["errors"] and roots == [b["skill"]], "lint errors=%s；ZIP 根目录=%s" % (b["lint"]["errors"], roots),
                  paths=[R.rel(b["skill_zip"]), R.rel(b["skill_dir"])])
    R.case("CORE-007", "CORE", "编译 WorkBuddy Brand Skill（lint + 单根 ZIP）", "lint 无错误，ZIP 只有一个根目录", "P0", skill)

    def portable():
        b = _fx(R, "brand-alpha")["build"]
        pd = Path(b["portable_dir"])
        need = ["DESIGN.md", "brand-ir.json", "tokens.json", "tokens.css", "README.md", "asset-manifest.json", "font-manifest.json"]
        dm = (pd / "DESIGN.md").read_text(encoding="utf-8")
        tj = read_json(pd / "tokens.json")
        good = all((pd / n).is_file() for n in need) and dm.startswith("---\n") and tj["color"]["primary"]["$type"] == "color"
        return ok(good, "文件齐全=%s；DESIGN.md 有 frontmatter=%s；DTCG $type=%s" % (
            all((pd / n).is_file() for n in need), dm.startswith("---\n"), tj["color"]["primary"]["$type"]), paths=[R.rel(pd)])
    R.case("CORE-008", "CORE", "Portable Design System（DESIGN.md + DTCG tokens + CSS）", "全部文件生成且格式正确", "P0", portable)

    def preview():
        b = _fx(R, "brand-alpha")["build"]
        pv = Path(b["preview_dir"])
        files = sorted(p.name for p in pv.glob("*.html"))
        offline = all(not qa.EXTERNAL.search(p.read_text(encoding="utf-8")) for p in pv.glob("*.html"))
        return ok(files == ["onepager.html", "poster.html"] and offline, "预览 %s；离线=%s" % (files, offline),
                  paths=[R.rel(pv / f) for f in files])
    R.case("CORE-009", "CORE", "生成可离线打开的 Preview", "poster.html 与 onepager.html，无外部资源", "P1", preview)

    def sot():
        res = [r for r in _fx(R, "brand-alpha")["build"]["qa_results"] if r["check"] == "sot.primary_consistent"]
        return ok(res and res[0]["result"] == "PASS", json.dumps(res[0]["detail"] if res else {}, ensure_ascii=False))
    R.case("CORE-010", "CORE", "单一事实来源：主色在 tokens.json / tokens.css / references / DESIGN.md / Preview 一致", "5 处一致", "P0", sot)

    def repro():
        a = run_fixture("brand-alpha", R.work / "repro-a")
        b = run_fixture("brand-alpha", R.work / "repro-b")
        da, db = _normalized_tree(a["build"]), _normalized_tree(b["build"])
        diff = sorted(k for k in set(da) | set(db) if da.get(k) != db.get(k))
        return ok(not diff and a["build"]["build_id"] == b["build"]["build_id"],
                  "比较 %d 个文件（排除 generated_at）；差异 %s；build_id %s / %s" % (len(da), diff or "无", a["build"]["build_id"], b["build"]["build_id"]))
    R.case("CORE-011", "CORE", "同一输入两次构建结果可复现", "规范化后逐文件一致", "P1", repro)

    def selfcheck():
        sk = Path(_fx(R, "brand-alpha")["build"]["skill_dir"])
        tmp = R.work / "selfcheck" / sk.name
        shutil.copytree(sk, tmp)
        p1 = subprocess.run([sys.executable, str(tmp / "scripts" / "selfcheck.py")], capture_output=True, text=True, encoding="utf-8", errors="replace", env=_child_env())
        (tmp / "references" / "color.md").write_text("tampered", encoding="utf-8")
        p2 = subprocess.run([sys.executable, str(tmp / "scripts" / "selfcheck.py")], capture_output=True, text=True, encoding="utf-8", errors="replace", env=_child_env())
        good = p1.returncode == 0 and "overall: MATCH" in p1.stdout and p2.returncode == 1 and "MISMATCH" in p2.stdout
        return ok(good, "原样：exit=%d %s；篡改后：exit=%d %s" % (p1.returncode, "MATCH" if "overall: MATCH" in p1.stdout else "?",
                                                         p2.returncode, "MISMATCH" if "MISMATCH" in p2.stdout else "?"),
                  cmds=["python scripts/selfcheck.py（Brand Skill 内）"])
    R.case("CORE-012", "CORE", "Brand Skill 自检：原样 MATCH，篡改后 MISMATCH", "两种情况都被正确识别", "P1", selfcheck)

    def collect():
        paths = []
        for name in ("brand-alpha", "brand-beta", "brand-gamma-new"):
            b = _fx(R, name)["build"]
            for key in ("skill_zip", "portable_zip"):
                dst = R.art / Path(b[key]).name
                shutil.copyfile(b[key], dst)
                paths.append(R.rel(dst))
            pv = R.art / ("preview-%s" % name)
            shutil.copytree(b["preview_dir"], pv, dirs_exist_ok=True)
            paths.append(R.rel(pv))
            src_rep = Path(b["skill_dir"]).parents[1] / "source-report" / "source-report.md"
            shutil.copyfile(src_rep, R.art / ("source-report-%s.md" % name))
        return ok(len(paths) == 9, "已复制 %d 个产物到 artifacts/" % len(paths), paths=paths)
    R.case("CORE-013", "CORE", "Alpha / Beta / Gamma 的 Brand Skill ZIP、Portable ZIP、Preview 已输出", "产物齐全", "P1", collect)


def _copy_ir_with(R, changes):
    ws = R.work / "schema-test"
    shutil.rmtree(ws, ignore_errors=True)
    shutil.copytree(_fx(R, "brand-beta")["ws"], ws)
    p = ws / "brand-ir" / "brand-ir.json"
    data = read_json(p)
    data.update(changes)
    write_json(p, data)
    return ws


def _normalized_tree(build):
    out = {}
    for base in (Path(build["skill_dir"]), Path(build["portable_dir"])):
        for p in sorted(base.rglob("*")):
            if p.is_file():
                text = p.read_bytes().decode("utf-8", errors="replace")
                text = re.sub(r'"generated_at": "[^"]*"', '"generated_at": "<T>"', text)
                out["%s/%s" % (base.name, p.relative_to(base).as_posix())] = sha256_bytes(text.encode("utf-8"))
    return out


# ---------------------------------------------------------------- QA

def _qa_tests(R):
    def wcag():
        cases = [("#000000", "#FFFFFF", 21.0, "text", "PASS"), ("#777777", "#FFFFFF", 4.48, "text", "WARNING"),
                 ("#777777", "#FFFFFF", 4.48, "large", "PASS"), ("#1F4FD8", "#FFFFFF", 6.63, "text", "PASS"),
                 ("#F59E0B", "#FFFFFF", 2.15, "ui", "FAIL")]
        rows = []
        good = True
        for fg, bg, want, kind, grade in cases:
            r = round(C.contrast(fg, bg), 2)
            g = C.grade(r, kind)
            rows.append("%s/%s=%.2f %s" % (fg, bg, r, g))
            good &= abs(r - want) <= 0.01 and g == grade
        return ok(good, "; ".join(rows))
    R.case("QA-001", "QA", "WCAG 对比度计算与已知基准一致", "21:1、4.48:1、6.63:1、2.15:1 及分级正确", "P0", wcag)

    def core_pairs():
        out = []
        good = True
        for name in ("brand-alpha", "brand-beta", "brand-gamma-new"):
            ir1, _ = W.load(_fx(R, name)["ws"])
            rows = IR.contrast_table(ir1)
            fails = [r["name"] for r in rows if r["result"] == "FAIL" and r.get("core")]
            good &= not fails
            out.append("%s: %d 组，核心 FAIL %s" % (name, len(rows), fails or "无"))
        return ok(good, "；".join(out))
    R.case("QA-002", "QA", "Alpha / Beta / Gamma 核心配色组合达到 AA", "无核心 FAIL", "P0", core_pairs)

    def lowc():
        ws = R.work / "low-contrast"
        W.init(MALFORMED / "low-contrast.json", ws, force=True)
        for g in ("G1", "G2"):
            W.gate(ws, g, "KEEP")
        blocked, msg = expect_error(lambda: W.gate(ws, "G3", "KEEP"), "E_GATE_BLOCKED")
        W.gate(ws, "G3", "CHANGE", {"override.body-text/page": "测试：用户坚持使用浅灰正文"})
        W.gate(ws, "G3", "CHANGE", {"override.body-text/surface": "测试：用户坚持使用浅灰正文"})
        W.gate(ws, "G3", "KEEP")
        ir1, _ = W.load(ws)
        ov = [o["pair"] for o in ir1["design_system"]["accessibility"]["overrides"]]
        rows = {r["name"]: r["result"] for r in IR.contrast_table(ir1)}
        good = blocked and "body-text/page" in ov and rows.get("body-text/page") == "USER_OVERRIDE"
        return ok(good, "G3 被拦截：%s；override 后状态 %s；记录 %s" % (msg, rows.get("body-text/page"), ov))
    R.case("QA-003", "QA", "低对比度核心组合阻止放行，USER_OVERRIDE 留痕", "G3 被拦截；用户坚持后记录 USER_OVERRIDE", "P0", lowc)

    def unapproved():
        b = _fx(R, "brand-alpha")["build"]
        ir1, _ = W.load(_fx(R, "brand-alpha")["ws"])
        poster = Path(b["preview_dir"]) / "poster.html"
        clean = qa.unapproved_colors(poster.read_text(encoding="utf-8"), qa.palette(ir1))
        dirty = qa.unapproved_colors(poster.read_text(encoding="utf-8") + "<style>.x{color:#123456}</style>", qa.palette(ir1))
        sk = Path(b["skill_dir"])
        tmp = R.work / "inject.html"
        tmp.write_text("<p style=\"color:#123456;font-family:Comic Sans MS\">x</p>", encoding="utf-8")
        p = subprocess.run([sys.executable, str(sk / "scripts/validate_brand.py"), str(tmp)], capture_output=True, text=True, encoding="utf-8", errors="replace", env=_child_env())
        return ok(not clean and dirty == ["#123456"] and p.returncode == 1,
                  "原始预览未批准颜色 %s；注入后检出 %s；Brand Skill 的 validate_brand.py exit=%d" % (clean or "无", dirty, p.returncode))
    R.case("QA-004", "QA", "检测未批准颜色（预览与 Brand Skill 校验脚本）", "原始无违规；注入的颜色被检出", "P1", unapproved)

    def forbidden():
        b = _fx(R, "brand-alpha")["build"]
        res = {r["check"]: r["result"] for r in b["qa_results"]}
        keys = [k for k in res if k.endswith("accent_not_text")]
        ir1, _ = W.load(_fx(R, "brand-alpha")["ws"])
        injected = qa.brand_qa(ir1, preview_dir=_inject_accent_text(R, b["preview_dir"]))
        caught = any(r["check"].endswith("accent_not_text") and r["result"] == "FAIL" for r in injected)
        return ok(keys and all(res[k] == "PASS" for k in keys) and caught, "原始：%s；注入 color:var(--color-accent) 后被检出=%s" % ({k: res[k] for k in keys}, caught))
    R.case("QA-005", "QA", "禁止规则：强调色不得用作文字", "原始通过；违规被检出", "P2", forbidden)

    def fonts():
        ws = R.work / "unknown-font"
        W.init(FIXTURES / "brand-beta.json", ws, force=True)
        for g in ("G1", "G2"):
            W.gate(ws, g, "KEEP")
        W.gate(ws, "G3", "CHANGE", {"font.heading": "Unknown Display X"})
        ir1, _ = W.load(ws)
        f = next(x for x in ir1["fonts"] if x["role"] == "heading")
        fam = next(x for x in ir1["design_system"]["typography"]["families"] if x["role"] == "heading")
        good = fam["fallbacks"][-1] in ("sans-serif", "serif") and f["license"].startswith("UNKNOWN") and not f["bundled"] and not f["redistribution_allowed"]
        return ok(good, "未知字体回退栈=%s；许可=%s；bundled=%s" % (fam["fallbacks"], f["license"], f["bundled"]))
    R.case("QA-006", "QA", "字体缺失或未知时有回退栈且不打包", "回退栈以通用字族结尾；许可标为未知；不打包", "P1", fonts)

    def assets():
        b = _fx(R, "brand-alpha")["build"]
        sk = Path(b["skill_dir"])
        man = read_json(sk / "templates/assets/asset-manifest.json")
        inc = {m["id"]: m["included"] for m in man}
        files = sorted(p.name for p in (sk / "templates/assets").glob("*.svg"))
        pfiles = sorted(p.name for p in (Path(b["portable_dir"]) / "assets").glob("*"))
        good = inc == {"logo-main": True, "pattern-3p": False} and files == ["alpha-logo.svg"] and pfiles == ["alpha-logo.svg"]
        return ok(good, "manifest=%s；Skill 内 SVG=%s；Portable=%s" % (inc, files, pfiles), paths=[R.rel(sk / "templates/assets/asset-manifest.json")])
    R.case("QA-007", "QA", "未授权资产不打包，manifest 记录排除原因", "只打包 user-owned Logo", "P0", assets)

    def contra():
        good, msg = expect_error(lambda: W.init(MALFORMED / "contradictory-rules.json", R.work / "contra", force=True), "E_IR_INVALID")
        return ok(good and "矛盾" in msg, msg)
    R.case("QA-008", "QA", "检测互相矛盾的规则（MUST vs NEVER）", "被拒绝并指出冲突规则", "P1", contra)

    def nofonts():
        found = []
        for name in ("brand-alpha", "brand-beta", "brand-gamma-new"):
            b = _fx(R, name)["build"]
            for base in (b["skill_dir"], b["portable_dir"]):
                found += [p.name for p in Path(base).rglob("*") if p.suffix.lower() in package.FONT_EXT]
        return ok(not found, "字体文件：%s" % (found or "无"))
    R.case("QA-009", "QA", "所有输出中不含字体文件", "无 .ttf/.otf/.woff 等", "P0", nofonts)

    def complete():
        res = {r["check"]: r for r in _fx(R, "brand-beta")["build"]["qa_results"]}
        r = res.get("skill.required_references")
        return ok(r and r["result"] == "PASS", "缺失 references：%s" % (r["detail"] if r else "?"))
    R.case("QA-010", "QA", "Brand Skill 内容完整（17 个 references）", "全部存在", "P1", complete)


def _inject_accent_text(R, preview_dir):
    d = R.work / "accent-inject"
    shutil.copytree(preview_dir, d, dirs_exist_ok=True)
    p = d / "poster.html"
    p.write_text(p.read_text(encoding="utf-8").replace("</style>", ".bad{color:var(--color-accent)}</style>"), encoding="utf-8")
    return d


# ---------------------------------------------------------------- SEC

def _sec_tests(R):
    def xss():
        ws = R.work / "xss"
        W.init(MALFORMED / "xss-brand.json", ws, force=True)
        for g in ("G1", "G2", "G3", "G4"):
            W.gate(ws, g, "KEEP")
        W.preview(ws)
        for g in ("G5", "G6"):
            W.gate(ws, g, "KEEP")
        b = W.build(ws, force=True)
        texts = [p.read_text(encoding="utf-8") for p in Path(b["preview_dir"]).glob("*.html")]
        texts += [p.read_text(encoding="utf-8") for p in Path(b["skill_dir"]).rglob("*.md")]
        texts.append((Path(b["portable_dir"]) / "DESIGN.md").read_text(encoding="utf-8"))
        raw = [t for t in texts if "<script>alert" in t or "<img src=x" in t]
        escaped = any("&lt;script&gt;" in t for t in texts)
        return ok(not raw and escaped, "未转义出现次数=%d；已转义=%s" % (len(raw), escaped), paths=[R.rel(b["preview_dir"])])
    R.case("SEC-001", "SEC", "恶意 HTML 字符串被转义", "输出中没有可执行的 <script>/<img onerror>", "P0", xss)
    for cid, fname, code, obj in (("SEC-002", "path-traversal.json", "E_PATH", "资产路径穿越（../）被拒绝"),
                                  ("SEC-003", "absolute-path.json", "E_PATH", "资产绝对路径被拒绝"),
                                  ("SEC-004", "bad-slug.json", "E_SLUG", "非法 slug（../evil）被拒绝"),
                                  ("SEC-006", "duplicate-rule-ids.json", "E_IR_INVALID", "重复规则 ID 被拒绝"),
                                  ("SEC-007", "frontmatter-injection.json", "E_FIELD", "品牌名中的换行（frontmatter 注入）被拒绝"),
                                  ("SEC-013", "css-injection.json", "E_FONT_NAME", "字体名中的 CSS/HTML 注入被拒绝")):
        R.case(cid, "SEC", obj, "返回 %s，不产生输出" % code, "P0" if cid != "SEC-006" else "P1",
               lambda fname=fname, code=code, cid=cid: (lambda r: ok(r[0] and not (R.work / cid / "exports").exists(), r[1]))(
                   expect_error(lambda: W.init(MALFORMED / fname, R.work / cid, force=True), code)))

    def badjson():
        code, so, se, shown = R.sub("init", "--brief", MALFORMED / "invalid-json.json", "--workspace", R.work / "badjson")
        data = json.loads(so) if so.strip().startswith("{") else {}
        good = code == 2 and data.get("error", {}).get("code") == "E_INVALID_JSON" and "Traceback" not in (so + se)
        return ok(good, "exit=%d code=%s traceback=%s" % (code, data.get("error", {}).get("code"), "Traceback" in (so + se)), cmds=[shown])
    R.case("SEC-005", "SEC", "无效 JSON 优雅失败", "退出码 2、结构化错误、无 Traceback", "P1", badjson)

    def svg():
        ws = R.work / "svg"
        W.init(MALFORMED / "malicious-svg.json", ws, force=True)
        ir1, _ = W.load(ws)
        a = ir1["assets"][0]
        return ok(a["include"] is False and "SVG" in a["notes"], "include=%s notes=%s" % (a["include"], a["notes"]))
    R.case("SEC-008", "SEC", "含脚本的 SVG 不被纳入", "include=false 并说明原因", "P0", svg)

    def overwrite():
        res = _fx(R, "brand-beta")
        ws = R.work / "overwrite"
        shutil.copytree(res["ws"], ws)
        target = Path(res["build"]["skill_dir"].replace(str(res["ws"]), str(ws)))
        man = target / "templates" / "build-manifest.json"
        data = read_json(man)
        data["build_id"] = "user-existing"
        write_json(man, data)
        before = sha256_bytes(man.read_bytes())
        good, msg = expect_error(lambda: W.build(ws), "E_EXISTS")
        after = sha256_bytes(man.read_bytes())
        return ok(good and before == after, "%s；原文件未被改动=%s" % (msg, before == after))
    R.case("SEC-009", "SEC", "不覆盖已存在的不同版本 Skill", "返回 E_EXISTS，原文件不变", "P0", overwrite)

    def nonet():
        bad = []
        for p in (SKILL_ROOT / "scripts").rglob("*.py"):
            t = p.read_text(encoding="utf-8")
            for mod in ("socket", "urllib", "http.client", "requests", "ftplib", "smtplib"):
                if re.search(r"^\s*(import|from)\s+%s\b" % re.escape(mod), t, re.M):
                    bad.append("%s:%s" % (p.name, mod))
        for p in (TEMPLATES / "brand-skill" / "scripts").glob("*.tmpl"):
            if re.search(r"^\s*(import|from)\s+(socket|urllib|http\.client|requests)\b", p.read_text(encoding="utf-8"), re.M):
                bad.append(p.name)
        return ok(not bad, "网络模块引用：%s" % (bad or "无"))
    R.case("SEC-010", "SEC", "不联网（静态检查网络模块）", "没有任何网络模块导入", "P0", nonet)

    def confined():
        integ = package_integrity()
        inside = all(R.rel(p).startswith("artifacts") for p in R.art.rglob("*"))
        unchanged = integ.get("ok", True) or "reason" in integ
        return ok(inside and unchanged, "产物均在报告目录内=%s；Skill 自身文件未被修改=%s" % (inside, unchanged))
    R.case("SEC-011", "SEC", "输出限定在报告目录，Skill 自身不被修改", "全部产物在 <run-dir>/artifacts", "P1", confined)
    R.case("SEC-012", "SEC", "报告脱敏：不出现用户主目录绝对路径", "报告中只有 <HOME>/<RUN_DIR> 占位", "P1",
           lambda: {"result": "NOT_TESTED", "actual": "在报告写出后检查"})


REPORT_FILES = ("TEST_REPORT.md", "results.json", "issues.md", "environment.json", "artifacts-manifest.json")
AGENT_NOTES = "agent-notes"
TEXT_SUFFIXES = {".md", ".txt", ".json", ".log", ".csv"}


def _agent_note_files(out):
    d = Path(out) / AGENT_NOTES
    if not d.is_dir():
        return []
    return [p for p in sorted(d.rglob("*")) if p.is_file() and p.suffix.lower() in TEXT_SUFFIXES]


def _redaction_map(out):
    return {"<RUN_DIR>": str(Path(out).resolve()), "<SKILL>": str(SKILL_ROOT), "<CWD>": str(Path.cwd().resolve())}


def report_leaks(out):
    found = {}
    files = [Path(out) / n for n in REPORT_FILES] + _agent_note_files(out)
    for f in files:
        if f.is_file():
            hit = leaks(f.read_text(encoding="utf-8", errors="replace"), _redaction_map(out))
            if hit:
                found[f.relative_to(Path(out)).as_posix()] = len(hit)
    return found


def _post_redaction_check(R):
    found = report_leaks(R.out)
    for c in R.cases:
        if c["id"] == "SEC-012":
            c.update(ok(not found, "检查 %d 个报告文件 + agent-notes（Windows/POSIX、正反斜杠、JSON 转义、盘符大小写、用户名路径段）；泄漏：%s" % (
                len(REPORT_FILES), found or "无"), fix="运行 finalize 命令对 agent-notes 脱敏；或检查 util.redact 是否覆盖该路径形式"))
            c["runtime_context"] = R.ctx


# ---------------------------------------------------------------- INS / MB / PP / UX

def _ins_tests(R):
    def no_h5():
        hits = []
        for p in list((SKILL_ROOT / "scripts").rglob("*.py")):
            t = p.read_text(encoding="utf-8")
            for pat in ("." + "workbuddy", "Application" + " Support", "App" + "Data", "." + "codebuddy"):
                if pat in t:
                    hits.append("%s:%s" % (p.name, pat))
        return ok(not hits, "代码中出现 WorkBuddy 安装目录的痕迹：%s" % (hits or "无"))
    R.case("INS-000", "INS", "代码中没有 H5（直接写入 WorkBuddy 内部 Skill 目录）", "无相关路径", "P0", no_h5)
    steps = ["阅读 references/installation-handoff.md", "向用户展示摘要并取得明确确认", "执行对应方式", "新会话中运行 Brand Skill 的 selfcheck"]
    for cid, obj, et in (("INS-001", "H1：原生安装工具（检查 Agent 工具列表中是否存在）", "AGENT"),
                         ("INS-002", "H2：交给内置 Skill Creator 原样安装（检查是否改写）", "AGENT"),
                         ("INS-003", "H3：用户发一句话触发原生安装", "MANUAL"),
                         ("INS-004", "H4：通过 UI 导入 ZIP", "MANUAL")):
        R.pending(cid, "INS", obj, "安装成功，selfcheck=MATCH；或如实记录 BLOCKED", "P1", et, "NOT_TESTED", "需要在 WorkBuddy 中执行", steps)
    R.pending("INS-005", "INS", "安装后 Brand Skill selfcheck=MATCH、版本与关键规则一致", "MATCH", "P0", "AGENT", "NOT_TESTED",
              "需要先完成 INS-001..004 中至少一项", steps)
    R.pending("INS-006", "INS", "安装前已向用户展示摘要并取得明确确认", "有确认记录", "P0", "AGENT", "NOT_TESTED", "需要 Agent 记录", steps)
    R.pending("INS-007", "INS", "记录 designbuddy-qa 本身是用哪种方式安装的（对话中附 ZIP 文件 / 客户端 UI 导入 / 其他），以及是否由平台完成", "如实记录；这是已知能装上本地 ZIP 的路径", "P1", "MANUAL", "NOT_TESTED",
              "需要用户说明", ["询问用户：你是怎样把 designbuddy-qa 装进 WorkBuddy 的？", "根据 PKG-008：平台写入了 _user_meta.json 即说明由平台机制安装"])


def _mb_tests(R):
    def desc():
        out, good = [], True
        for name in ("brand-alpha", "brand-beta"):
            sk = Path(_fx(R, name)["build"]["skill_dir"])
            fm = package.parse_frontmatter((sk / "SKILL.md").read_text(encoding="utf-8"))
            ir1, _ = W.load(_fx(R, name)["ws"])
            names = [ir1["brand"]["name"]["value"]] + ir1["brand"]["aliases"]["value"]
            has = all(n in fm["description"] for n in names)
            rule = "不要使用" in fm["description"] and "不要擅自套用" in (sk / "SKILL.md").read_text(encoding="utf-8")
            good &= has and rule
            out.append("%s: 名称/别名齐全=%s 消歧规则=%s" % (name, has, rule))
        return ok(good, "；".join(out))
    R.case("MB-001", "MB", "Alpha / Beta 的 description 含名称、别名，SKILL.md 含消歧规则", "全部包含", "P1", desc)

    def overlap():
        sets = []
        for name in ("brand-alpha", "brand-beta"):
            ir1, _ = W.load(_fx(R, name)["ws"])
            sets.append({a.lower() for a in ir1["brand"]["aliases"]["value"]})
        inter = sets[0] & sets[1]
        return ok(not inter, "别名交集：%s" % (sorted(inter) or "无"))
    R.case("MB-002", "MB", "Alpha / Beta 别名不重叠", "交集为空", "P1", overlap)
    for cid, obj in (("MB-003", "独立新会话：「给 Alpha Demo 做一份 PPT 封面」只触发 Alpha"),
                     ("MB-004", "独立新会话：「做一份 PPT」不擅自套用任何品牌（应先询问）"),
                     ("MB-005", "独立新会话：「把 Beta Demo 的这段文档改成 Alpha Demo 风格」source=Beta、target=Alpha")):
        R.pending(cid, "MB", obj, "见 next-session-prompts.md", "P1", "MANUAL", "NOT_TESTED",
                  "PENDING_MANUAL：必须在独立新会话中执行，本会话内的模拟不算数", ["安装 Alpha/Beta Brand Skill（需用户确认）", "按 next-session-prompts.md 在新会话中执行"])


def _pp_tests(R):
    def local():
        res = _fx(R, "brand-alpha")
        good = res["ok"] and (TEMPLATES / "brand-skill/SKILL.md.tmpl").is_file()
        return ok(good, "当前安装环境中：模板可读、脚本可执行、产物已写出。只代表当前安装形态（见 ENV-008），不代表付费加密形态")
    R.case("PP-001", "PP", "当前安装形态下：读取模板、执行脚本、生成文件", "全部可用", "P1", local)
    for cid, obj in (("PP-002", "市场付费加密形态（开发者账号）：资源、脚本、生成器可用性"),
                     ("PP-003", "市场付费加密形态（普通购买者账号）：资源、脚本、生成器可用性")):
        R.pending(cid, "PP", obj, "需要真实付费加密环境", "P1", "MANUAL", "BLOCKED", PP_BLOCK,
                  ["由产品负责人决定是否发布付费测试版", "在付费加密安装中运行 QA RUN ALL"])


def _ux_tests(R):
    def decisions():
        n = max(_fx(R, x)["decisions"] for x in ("brand-alpha", "brand-beta", "brand-gamma-new"))
        total = n + 2
        return ok(total <= 10, "最短路径用户决策：Gate 决策 %d 次 + 安装确认 1 次 + 选择保存目录 ≤1 次 = %d" % (n, total), partial=True,
                  fix="合并 Gate 或提供一键确认默认值")
    R.case("UX-001", "UX", "最短路径的用户决策次数", "≤ 10 次", "P2", decisions)
    R.case("UX-002", "UX", "用户无需编写代码或临时设计通用模板", "三条路径只用数据决策完成", "P1",
           lambda: ok(all(_fx(R, x)["ok"] for x in ("brand-alpha", "brand-beta", "brand-gamma-new")),
                      "三条路径均由预置编译器完成，用户只做 KEEP/CHANGE 决策"))

    def speed():
        secs = {x: _fx(R, x)["seconds"] for x in ("brand-alpha", "brand-beta", "brand-gamma-new")}
        return ok(all(s < 30 for s in secs.values()), "构建耗时（秒）：%s" % secs)
    R.case("UX-003", "UX", "构建耗时", "每个品牌 < 30 秒", "P3", speed)

    def recover():
        ws = R.work / "recover"
        W.init(MALFORMED / "low-contrast.json", ws, force=True)
        W.gate(ws, "G1", "KEEP")
        W.gate(ws, "G2", "KEEP")
        failed, _m = expect_error(lambda: W.gate(ws, "G3", "KEEP"), "E_GATE_BLOCKED")
        st = W.status(ws)
        again, _m2 = expect_error(lambda: W.init(MALFORMED / "low-contrast.json", ws), "E_EXISTS")
        W.gate(ws, "G3", "CHANGE", {"color.ink": "#111827"})
        W.gate(ws, "G3", "KEEP")
        return ok(failed and not st["errors"] and again and W.status(ws)["gates"]["G3"] == "KEEP",
                  "拦截后工作区仍有效；重复 init 被拒绝；修正 color.ink 后 G3 通过")
    R.case("UX-004", "UX", "错误后可恢复，不破坏工作区", "失败后可修正并继续", "P1", recover)


# ---------------------------------------------------------------- reports

def weak_evidence(cases):
    """AGENT/MANUAL PASS results whose evidence cannot support the claim."""
    out = []
    for c in cases:
        if c["execution_type"] == "SCRIPT" or c["result"] != "PASS":
            continue
        if not c.get("evidence"):
            out.append("%s：PASS 但没有证据" % c["id"])
        elif c["id"] in INS_IDS and not c.get("commands_or_actions"):
            out.append("%s：安装类 PASS 没有记录实际执行的工具调用或命令" % c["id"])
    return out


def summarize(cases):
    counts = {r: sum(1 for c in cases if c["result"] == r) for r in RESULTS}
    script = [c for c in cases if c["execution_type"] == "SCRIPT"]
    sp = sum(1 for c in script if c["result"] == "PASS")
    issues = {s: sum(1 for c in cases if c["severity"] == s and c["result"] in ("FAIL", "PARTIAL")) for s in ("P0", "P1", "P2", "P3")}
    unverified = [c["id"] for c in cases if c["result"] in ("BLOCKED", "NOT_TESTED")]
    script_ok = all(c["result"] == "PASS" for c in script)
    ins_ok = any(c["id"] in ("INS-001", "INS-002", "INS-003", "INS-004") and c["result"] == "PASS" for c in cases) and \
        any(c["id"] == "INS-005" and c["result"] == "PASS" for c in cases)
    agent_ok = all(c["result"] == "PASS" for c in cases if c["id"] in ("ENV-007", "ENV-008", "ENV-009", "INS-006"))
    weak = weak_evidence(cases)
    local_passed = script_ok and ins_ok and agent_ok and not weak and issues["P0"] == 0 and issues["P1"] == 0
    return {"counts": counts, "total": len(cases), "script_total": len(script), "script_pass": sp,
            "script_pass_rate": round(100.0 * sp / len(script), 1) if script else 0.0, "issues": issues, "unverified": unverified,
            "fix_round_recommended": any(issues.values()) or bool(weak), "weak_evidence": weak,
            "states": {"LOCAL_QA_PASSED": "YES" if local_passed else "NO",
                       "READY_FOR_PLATFORM_SUBMISSION": "NO（QA 候选版不用于上架）",
                       "PLATFORM_PARSE_PASSED": "NOT_REACHED", "REVIEW_APPROVED": "NOT_REACHED",
                       "PAID_ENCRYPTED_RUNTIME_VERIFIED": "NOT_REACHED"}}


def write_reports(out, run_id, cases, env):
    out = Path(out)
    red = _redaction_map(out)
    clean = redact_obj(cases, red)
    s = summarize(clean)
    env_r = redact_obj(env, red)
    write_json(out / "environment.json", env_r)
    write_json(out / "results.json", {"run_id": run_id, "designbuddy": DESIGNBUDDY_VERSION, "skill": SKILL_NAME,
                                      "generated_at": now_iso(), "summary": s, "cases": clean})
    arts = []
    art = out / "artifacts"
    if art.is_dir():
        for p in sorted(art.rglob("*")):
            if p.is_file():
                arts.append({"path": p.relative_to(out).as_posix(), "bytes": p.stat().st_size, "sha256": sha256_bytes(p.read_bytes())})
    write_json(out / "artifacts-manifest.json", {"run_id": run_id, "designbuddy": DESIGNBUDDY_VERSION, "artifacts": arts})
    write_text(out / "TEST_REPORT.md", _report_md(run_id, clean, s, env_r))
    write_text(out / "issues.md", _issues_md(clean))
    write_text(out / "next-session-prompts.md", NEXT_SESSION)


def _report_md(run_id, cases, s, env):
    L = ["# DesignBuddy QA 测试报告", "",
         "- Run ID：`%s`" % run_id, "- DesignBuddy：%s（%s）" % (DESIGNBUDDY_VERSION, SKILL_NAME),
         "- 环境：%s · Python %s · WorkBuddy 版本：%s" % (env["platform"], env["python"]["version"], env["workbuddy_version"]),
         "- 安装包指纹：version %s · package-manifest SHA-256 `%s`" % ((env.get("package") or {}).get("version"), (env.get("package") or {}).get("manifest_sha256")), "",
         "## 汇总", "",
         "| 指标 | 数值 |", "|---|---|",
         "| 用例总数 | %d |" % s["total"],
         "| PASS / FAIL / PARTIAL / BLOCKED / NOT_TESTED | %s |" % " / ".join(str(s["counts"][r]) for r in RESULTS),
         "| 自动化（SCRIPT）通过率 | %s%%（%d/%d） |" % (s["script_pass_rate"], s["script_pass"], s["script_total"]),
         "| 问题数 P0 / P1 / P2 / P3 | %s |" % " / ".join(str(s["issues"][k]) for k in ("P0", "P1", "P2", "P3")),
         "| 未验证项 | %d（%s） |" % (len(s["unverified"]), ", ".join(s["unverified"]) or "无"),
         "| 证据不足的 PASS | %s |" % ("；".join(s["weak_evidence"]) or "无"),
         "| 建议进入下一轮修复 | %s |" % ("是" if s["fix_round_recommended"] else "否"), "",
         "## 状态（互不替代）", "", "| 状态 | 结论 |", "|---|---|"]
    L += ["| %s | %s |" % (k, v) for k, v in s["states"].items()]
    L += ["", "> LOCAL_QA_PASSED 需要：全部 SCRIPT 用例 PASS，ENV-007/008/009、INS-006 已由 Agent 记录为 PASS，"
          "INS-001..004 至少一项 PASS（附实际工具调用或命令），INS-005 PASS，且没有证据不足的 PASS。", "", "## 用例", "",
          "| ID | 领域 | 类型 | 级别 | 结果 | 目标 | 实际 |", "|---|---|---|---|---|---|---|"]
    for c in cases:
        L.append("| %s | %s | %s | %s | **%s** | %s | %s |" % (c["id"], c["area"], c["execution_type"], c["severity"], c["result"],
                                                           c["objective"].replace("|", "/"), (c["actual"] or c["error_or_block_reason"]).replace("|", "/")[:160]))
    L += ["", "详细字段见 `results.json`；失败与阻塞见 `issues.md`；多品牌新会话测试见 `next-session-prompts.md`。", ""]
    return "\n".join(L)


def _issues_md(cases):
    L = ["# Issues", ""]
    bad = [c for c in cases if c["result"] in ("FAIL", "PARTIAL")]
    blk = [c for c in cases if c["result"] in ("BLOCKED", "NOT_TESTED")]
    L += ["## FAIL / PARTIAL（需要修复）", ""]
    for c in bad:
        L += ["### %s · %s · %s" % (c["id"], c["severity"], c["result"]), "", "- 目标：%s" % c["objective"], "- 预期：%s" % c["expected"],
              "- 实际：%s" % c["actual"], "- 复现：在 Skill 目录运行 `python scripts/designbuddy.py run-all --out <目录>`，查看该用例",
              "- 命令：%s" % (", ".join(c["commands_or_actions"]) or "见 qarunner.py 中的同名用例"),
              "- 建议修复：%s" % (c["suggested_fix"] or "—"), ""]
    if not bad:
        L += ["无。", ""]
    L += ["## BLOCKED / NOT_TESTED（需要外部条件，不算通过）", ""]
    for c in blk:
        L += ["- **%s** %s — %s（%s）" % (c["id"], c["result"], c["objective"], c["error_or_block_reason"])]
    return "\n".join(L) + "\n"


NEXT_SESSION = """# 多品牌独立新会话测试（MB-003 ~ MB-005）

前提：已在用户明确确认后安装 `alpha-demo-brand-system` 和 `beta-demo-brand-system`（见 artifacts/）。
每条测试都要**新开一个会话**，粘贴提示词，记录回复中实际使用的品牌、颜色、字体。

## MB-003（只触发 Alpha）

```
给 Alpha Demo 做一份 PPT 封面页和一页内容页的版式说明。
```
PASS：回复声明使用 Alpha Demo 品牌系统；主色 #1F4FD8；标题字体 Source Han Sans SC。

## MB-004（不擅自套用品牌）

```
做一份 PPT。
```
PASS：没有套用任何品牌，或先询问用户使用哪个品牌。FAIL：直接套用了 Alpha 或 Beta。

## MB-005（品牌转换）

```
这是 Beta Demo 的一段文档：「欢迎来到周末读书会，本期主题是城市散步。」请把它改成 Alpha Demo 的风格。
```
PASS：明确 source=Beta Demo、target=Alpha Demo；输出只使用 Alpha 的颜色（#1F4FD8 等）和字体。FAIL：混用 Beta 的颜色或字体。

## 回填结果

回到 QA 会话，让 Agent 执行（示例）：
```
python <designbuddy-qa>/scripts/designbuddy.py record --run <报告目录> --id MB-003 --result PASS --actual "<实际回复摘要>" --evidence "<截图文件名>" --context "新会话 / macOS / WorkBuddy x.y"
```
"""


def finalize(run_dir):
    """Last step of a QA run: redact agent-authored notes in place, regenerate reports, re-check leaks."""
    run_dir = Path(run_dir)
    data = read_json(run_dir / "results.json")
    red = _redaction_map(run_dir)
    changed = []
    for f in _agent_note_files(run_dir):
        text = f.read_text(encoding="utf-8", errors="replace")
        clean = redact(text, red)
        if clean != text:
            f.write_text(clean, encoding="utf-8")
            changed.append(f.relative_to(run_dir).as_posix())
    env = read_json(run_dir / "environment.json")
    write_reports(run_dir, data["run_id"], data["cases"], env)
    found = report_leaks(run_dir)
    for c in data["cases"]:
        if c["id"] == "SEC-012":
            c.update(ok(not found, "finalize 后检查报告文件 + agent-notes；已脱敏 agent-notes 文件：%s；剩余泄漏：%s" % (changed or "无", found or "无")))
    write_reports(run_dir, data["run_id"], data["cases"], env)
    return {"ok": not found, "redacted_agent_notes": changed, "leaks": found, "summary": summarize(data["cases"])}


def record(run_dir, cid, result, actual, evidence="", context="", reason="", commands=None):
    run_dir = Path(run_dir)
    data = read_json(run_dir / "results.json")
    if result not in RESULTS:
        raise DBError("E_RESULT", "result 只能是 %s" % " / ".join(RESULTS))
    case = next((c for c in data["cases"] if c["id"] == cid), None)
    if case is None:
        raise DBError("E_RECORD", "没有这个用例：%s" % cid)
    if case["execution_type"] == "SCRIPT":
        raise DBError("E_RECORD_SCRIPT", "%s 是脚本用例，结果只能由 QA Runner 产生，不能手工改写" % cid)
    if result == "PASS" and not (actual and (evidence or context)):
        raise DBError("E_RECORD", "PASS 必须提供实际结果，以及证据或运行上下文")
    if result == "BLOCKED" and not reason:
        raise DBError("E_RECORD", "BLOCKED 必须说明外部条件（--reason）")
    commands = [c for c in (commands or []) if c and c.strip()]
    if result == "PASS" and cid in INS_IDS and not commands:
        raise DBError("E_RECORD", "安装类用例 PASS 必须用 --commands 记录实际执行的工具调用或命令（谁执行、调用了什么）")
    if result == "PASS" and not evidence:
        raise DBError("E_RECORD", "PASS 必须提供 --evidence")
    case.update(result=result, actual=actual, evidence=evidence, error_or_block_reason=reason,
                commands_or_actions=commands or case.get("commands_or_actions", []),
                runtime_context=context or case["runtime_context"], recorded_at=now_iso())
    env = read_json(run_dir / "environment.json")
    write_reports(run_dir, data["run_id"], data["cases"], env)
    return {"ok": True, "id": cid, "result": result, "summary": summarize(data["cases"])}
