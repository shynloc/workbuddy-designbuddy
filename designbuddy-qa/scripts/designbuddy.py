#!/usr/bin/env python3
"""DesignBuddy QA command-line entry point.

All commands print one JSON object to stdout. Exit codes:
0 ok · 1 validation/QA failure · 2 usage or input error · 3 environment unsupported.

Commands:
  version
  env
  init        --brief FILE --workspace DIR [--force]
  status      --workspace DIR
  gate        --workspace DIR --gate G1..G6 --decision KEEP|CHANGE|REJECT [--set key=value ...] [--note TEXT]
  validate    --workspace DIR [--release]
  preview     --workspace DIR
  build       --workspace DIR [--force] [--deliver [--to DIR]]
  deliver     --workspace DIR | --run RUN [--to DIR]   (复制到 下载/DesignBuddy/…，不覆盖已有文件)
  fixture     --name brand-alpha|brand-beta|brand-gamma-new --workspace DIR   (runs a fixture end to end)
  run-all     [--out DIR]                     (QA RUN ALL)
  record      --run DIR --id TEST_ID --result R --actual TEXT [--evidence TEXT] [--context TEXT] [--reason TEXT] [--commands TEXT ...]
  finalize    --run DIR                       (QA 结束前最后一步：agent-notes 脱敏 + 重新检查泄漏)
  selftest
"""
import argparse
import json
import sys
from pathlib import Path

if sys.version_info < (3, 8):
    print(json.dumps({"ok": False, "error": {"code": "E_PYTHON", "message": "需要 Python 3.8 或更高版本"}}))
    sys.exit(3)

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True

import db_util as util  # noqa: E402
from db_util import DBError  # noqa: E402


def out(obj, code=0):
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:  # noqa: BLE001
        pass
    print(json.dumps(obj, ensure_ascii=False, indent=2, default=str))
    return code


def parse_set(pairs):
    patch = {}
    for p in pairs or []:
        if "=" not in p:
            raise DBError("E_USAGE", "--set 需要 key=value 格式：%s" % p)
        k, v = p.split("=", 1)
        patch[k.strip()] = v.strip()
    return patch


def _has_qa():
    return (Path(__file__).resolve().parent / "db_qarunner.py").is_file()


def main(argv=None):
    ap = argparse.ArgumentParser(prog="designbuddy", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("version")
    sub.add_parser("env")
    sub.add_parser("selftest")
    s = sub.add_parser("init"); s.add_argument("--brief", required=True); s.add_argument("--workspace", required=True); s.add_argument("--force", action="store_true")
    s = sub.add_parser("status"); s.add_argument("--workspace", required=True)
    s = sub.add_parser("gate"); s.add_argument("--workspace", required=True); s.add_argument("--gate", required=True)
    s.add_argument("--decision", required=True); s.add_argument("--set", action="append"); s.add_argument("--note", default="")
    s = sub.add_parser("validate"); s.add_argument("--workspace", required=True); s.add_argument("--release", action="store_true")
    s = sub.add_parser("preview"); s.add_argument("--workspace", required=True)
    s = sub.add_parser("build"); s.add_argument("--workspace", required=True); s.add_argument("--force", action="store_true")
    s.add_argument("--deliver", action="store_true", help="构建后把交付包复制到下载文件夹（或 --to 指定的目录）")
    s.add_argument("--to", default=None)
    s = sub.add_parser("deliver"); g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--workspace"); g.add_argument("--run", help="QA 报告目录：交付其中的 Brand Skill ZIP"); s.add_argument("--to", default=None)
    s = sub.add_parser("fixture"); s.add_argument("--name", required=True); s.add_argument("--workspace", required=True)
    s = sub.add_parser("run-all"); s.add_argument("--out", default=None)
    s = sub.add_parser("finalize"); s.add_argument("--run", required=True)
    s = sub.add_parser("record"); s.add_argument("--run", required=True); s.add_argument("--id", required=True)
    s.add_argument("--result", required=True); s.add_argument("--actual", required=True); s.add_argument("--evidence", default="")
    s.add_argument("--context", default=""); s.add_argument("--reason", default="")
    s.add_argument("--commands", action="append", default=[], help="实际执行的工具调用或命令（可重复）")
    try:
        args = ap.parse_args(argv)
    except SystemExit as e:
        return int(e.code or 0) and 2

    try:
        if args.cmd in (None, "version"):
            return out({"ok": True, "name": util.SKILL_NAME, "version": util.DESIGNBUDDY_VERSION, "schema_version": util.SCHEMA_VERSION})
        if args.cmd == "env":
            import db_runtime as runtime, db_deliver as deliver
            env = runtime.environment()
            d, how = deliver.downloads_dir()
            env["downloads"] = {"exists": d.is_dir(), "found_by": how}
            return out({"ok": True, "environment": env})
        if args.cmd == "selftest":
            import db_runtime as runtime
            res = runtime.package_integrity()
            res["installed_extras"] = runtime.installed_extras()
            return out(res, 0 if res["ok"] else 1)
        if args.cmd in ("fixture", "run-all", "record", "finalize") and not _has_qa():
            return out({"ok": False, "error": {"code": "E_UNAVAILABLE", "message": "此版本不包含 QA Runner"}}, 2)
        import db_workspace as W
        if args.cmd == "init":
            return out(W.init(args.brief, args.workspace, args.force))
        if args.cmd == "status":
            return out(W.status(args.workspace))
        if args.cmd == "gate":
            return out(W.gate(args.workspace, args.gate.upper(), args.decision.upper(), parse_set(args.set), args.note))
        if args.cmd == "validate":
            import db_ir as IR
            data, _ = W.load(args.workspace)
            rep = IR.validate(data, "release" if args.release else "draft")
            return out(dict(rep, ok=not rep["errors"]), 0 if not rep["errors"] else 1)
        if args.cmd == "preview":
            res = W.preview(args.workspace)
            return out(res, 0 if res["qa"]["passed"] else 1)
        if args.cmd == "build":
            res = W.build(args.workspace, args.force)
            if args.deliver and res["ok"]:
                import db_deliver as deliver
                try:
                    res["delivery"] = deliver.deliver(args.workspace, args.to)
                except DBError as e:
                    res["delivery"] = e.as_dict()
            return out(res, 0 if res["ok"] else 1)
        if args.cmd == "deliver":
            import db_deliver as deliver
            if args.run:
                return out(deliver.deliver_run(args.run, args.to))
            return out(deliver.deliver(args.workspace, args.to))
        if args.cmd == "fixture":
            import db_qarunner as qarunner
            res = qarunner.run_fixture(args.name, Path(args.workspace))
            return out(res, 0 if res.get("ok") else 1)
        if args.cmd == "run-all":
            import db_qarunner as qarunner
            res = qarunner.run_all(args.out)
            return out(res, 0)
        if args.cmd == "finalize":
            import db_qarunner as qarunner
            res = qarunner.finalize(args.run)
            return out(res, 0 if res["ok"] else 1)
        if args.cmd == "record":
            import db_qarunner as qarunner
            return out(qarunner.record(args.run, args.id, args.result, args.actual, args.evidence, args.context, args.reason, args.commands))
    except DBError as e:
        return out(e.as_dict(), 2)
    except Exception as e:  # noqa: BLE001 - never dump a traceback at the user
        return out({"ok": False, "error": {"code": "E_INTERNAL", "message": "%s: %s" % (type(e).__name__, e)}}, 2)
    return out({"ok": False, "error": {"code": "E_USAGE", "message": "未知命令"}}, 2)


if __name__ == "__main__":
    sys.exit(main())
