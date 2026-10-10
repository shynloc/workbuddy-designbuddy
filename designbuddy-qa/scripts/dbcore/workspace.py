"""DesignBuddy workspace: init, gates, preview, build. Local files only."""
import json
import shutil
from pathlib import Path

from . import engine, exporters, ir as IR, package, qa
from .util import (DBError, DESIGNBUDDY_VERSION, SCHEMA_VERSION, dump_json, now_iso, read_json,
                   resolve_inside, write_json, write_text)

NEXT = {
    "G1": "确认品牌基础（定位、受众、性格、语气）",
    "G2": "选择或确认视觉方向",
    "G3": "确认核心设计系统（颜色、字体、间距、无障碍）",
    "G4": "确认各媒介应用规则",
    "G5": "生成并审核 Preview",
    "G6": "确认最终导出",
}


def _paths(ws):
    ws = Path(ws)
    return {"ws": ws, "project": ws / "project.json", "ir": ws / "brand-ir" / "brand-ir.json",
            "history": ws / "brand-ir" / "history", "brief": ws / "sources" / "brief.json",
            "assets": ws / "sources" / "assets", "manifest": ws / "sources" / "source-manifest.json",
            "reviews": ws / "reviews", "exports": ws / "exports", "state": ws / ".designbuddy" / "state.json"}


def init(brief_path, ws, force=False):
    P = _paths(ws)
    if P["project"].exists() and not force:
        raise DBError("E_EXISTS", "工作区已存在项目，如需重新开始请换一个目录或使用 --force")
    brief_path = Path(brief_path)
    brief = read_json(brief_path)
    ir = engine.intake(brief)
    P["assets"].mkdir(parents=True, exist_ok=True)
    for a in ir["assets"]:
        try:
            src = resolve_inside(brief_path.parent, a["file"], "asset %s" % a["id"])
        except DBError as e:
            raise DBError(e.code, e.message)
        if not src.is_file():
            a["include"] = False
            a["notes"] = "文件不存在，未纳入"
            continue
        data = src.read_bytes()
        if b"<svg" in data[:4096].lower() and package.SVG_BAD.search(data.decode("utf-8", errors="replace")):
            a["include"] = False
            a["notes"] = "SVG 含脚本或事件属性，已拒绝纳入"
        dst = resolve_inside(P["assets"], a["file"])
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
    write_json(P["brief"], brief)
    write_json(P["manifest"], [dict(s, included_in_final=False) for s in ir["sources"]])
    write_json(P["project"], {"slug": ir["brand"]["slug"], "display_name": ir["brand"]["name"]["value"],
                              "path": ir["metadata"]["path"], "created_at": now_iso(),
                              "designbuddy_version": DESIGNBUDDY_VERSION, "schema_version": SCHEMA_VERSION,
                              "skill_name": exporters.skill_name(ir)})
    save(ws, ir, "init")
    return status(ws)


def load(ws):
    P = _paths(ws)
    if not P["ir"].is_file():
        raise DBError("E_NO_PROJECT", "工作区中没有 Brand IR，请先运行 init")
    data = read_json(P["ir"])
    if data.get("schema_version") != SCHEMA_VERSION:
        raise DBError("E_SCHEMA_VERSION", "Brand IR schema_version=%r，本版本只支持 %s" % (data.get("schema_version"), SCHEMA_VERSION))
    return data, read_json(P["brief"])


def save(ws, ir, label):
    P = _paths(ws)
    report = IR.validate(ir)
    if report["errors"]:
        raise DBError("E_IR_INVALID", "Brand IR 校验失败：%s" % report["errors"][0]["message"], {"errors": report["errors"][:10]})
    write_json(P["ir"], ir)
    P["history"].mkdir(parents=True, exist_ok=True)
    n = len(list(P["history"].glob("*.json"))) + 1
    write_json(P["history"] / ("%03d-%s.json" % (n, label)), ir)
    open_gate = next((g for g in IR.GATES if ir["gates"][g]["status"] != "KEEP"), None)
    write_json(P["state"], {"phase": open_gate or "DONE", "next_action_zh": NEXT.get(open_gate, "安装 Brand Skill 并运行 Smoke Test"),
                            "gates": {g: ir["gates"][g]["status"] for g in IR.GATES}, "updated_at": now_iso()})
    return report


def status(ws):
    ir, _brief = load(ws)
    rep = IR.validate(ir)
    return {"ok": True, "slug": ir["brand"]["slug"], "path": ir["metadata"]["path"],
            "gates": {g: ir["gates"][g]["status"] for g in IR.GATES},
            "candidates": ir.get("candidates", []), "conflicts": [c for c in ir.get("conflicts", []) if c["status"] == "open"],
            "provenance": engine.provenance_summary(ir)["counts"],
            "review_first": engine.provenance_summary(ir)["review_first"][:20],
            "errors": rep["errors"], "next": read_json(_paths(ws)["state"])}


def gate(ws, gate_id, decision, patch=None, note=""):
    ir, brief = load(ws)
    rec = engine.apply_gate(ir, brief, gate_id, decision, patch, note)
    save(ws, ir, "%s-%s" % (gate_id, decision.lower()))
    P = _paths(ws)
    P["reviews"].mkdir(parents=True, exist_ok=True)
    n = len(list(P["reviews"].glob("gate-*.json"))) + 1
    write_json(P["reviews"] / ("gate-%03d-%s.json" % (n, gate_id)), rec)
    return {"ok": True, "record": rec, "gates": {g: ir["gates"][g]["status"] for g in IR.GATES}}


def preview(ws):
    ir, _brief = load(ws)
    if ir["gates"]["G4"]["status"] != "KEEP":
        raise DBError("E_GATE_ORDER", "需要先确认 G4（应用规则）才能生成 Preview")
    out = _paths(ws)["exports"] / "preview"
    files = exporters.export_preview(ir, out)
    results = qa.brand_qa(ir, preview_dir=out)
    summ = qa.summarize(results)
    ir["metadata"]["preview"] = {"qa_passed": summ["passed"], "build_id": exporters.build_id(ir), "files": [f.name for f in files]}
    save(ws, ir, "preview")
    write_json(_paths(ws)["reviews"] / "qa-preview.json", {"summary": summ, "results": results})
    return {"ok": True, "files": [str(f) for f in files], "qa": summ, "results": results}


def build(ws, force=False):
    ir, _brief = load(ws)
    rep = IR.validate(ir, stage="release")
    if rep["errors"]:
        raise DBError("E_NOT_READY", "尚未满足导出条件：%s" % rep["errors"][0]["message"], {"errors": rep["errors"][:10]})
    P = _paths(ws)
    name = exporters.skill_name(ir)
    skill_root = P["exports"] / "workbuddy-skill"
    target = skill_root / name
    bid = exporters.build_id(ir)
    if target.exists():
        man = target / "templates" / "build-manifest.json"
        old = json.loads(man.read_text(encoding="utf-8")).get("build_id") if man.is_file() else None
        if old != bid and not force:
            raise DBError("E_EXISTS", "导出目录中已有不同版本的 %s（build %s），不会覆盖。确认后使用 --force" % (name, old))
        shutil.rmtree(target)
    sk, manifest = exporters.export_skill(ir, skill_root, P["assets"])
    lint = package.lint_skill(sk)
    zip_path, zip_sha = package.pack(sk, P["exports"] / ("%s-%s.zip" % (name, ir["version"]["skill"])))
    preview_dir = P["exports"] / "preview"
    exporters.export_preview(ir, preview_dir)
    portable = P["exports"] / "portable-design-system"
    if portable.exists():
        shutil.rmtree(portable)
    exporters.export_portable(ir, portable, P["assets"], preview_dir)
    pzip, psha = package.pack(portable, P["exports"] / ("%s-portable-design-system-%s.zip" % (ir["brand"]["slug"], ir["metadata"]["system_version"])),
                              "%s-portable-design-system" % ir["brand"]["slug"])
    write_text(P["exports"] / "source-report" / "source-report.md", exporters.source_report(ir))
    write_json(P["exports"] / "source-report" / "provenance.json", engine.provenance_summary(ir))
    results = qa.brand_qa(ir, sk, portable, preview_dir)
    summary = {"ok": not lint["errors"] and qa.summarize(results)["passed"], "skill": name, "skill_version": ir["version"]["skill"],
               "system_version": ir["metadata"]["system_version"], "build_id": bid,
               "skill_dir": str(sk), "skill_zip": str(zip_path), "skill_zip_sha256": zip_sha,
               "portable_dir": str(portable), "portable_zip": str(pzip), "portable_zip_sha256": psha,
               "preview_dir": str(preview_dir), "lint": lint, "qa": qa.summarize(results), "qa_results": results}
    write_text(P["reviews"] / "build-report.json", dump_json(summary))
    return summary
