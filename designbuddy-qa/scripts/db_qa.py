"""Deterministic Brand QA over exported artefacts. No model judgement involved."""
import json
import re
from pathlib import Path

from db_ir import contrast_table, rule_contradictions
from db_exporters import colors, v
from db_package import FONT_EXT

HEX_ANY = re.compile(r"#[0-9A-Fa-f]{6}\b|#[0-9A-Fa-f]{3}\b")
EXTERNAL = re.compile(r"(?:src|href)\s*=\s*[\"'](?:https?:)?//|@import\s+url\(\s*[\"']?(?:https?:)?//|url\(\s*[\"']?https?://", re.I)
REQUIRED_REFS = ("brand-core.md", "identity.md", "voice.md", "color.md", "typography.md", "spacing-layout.md",
                 "imagery.md", "accessibility.md", "ppt.md", "word.md", "excel.md", "web.md", "poster.md",
                 "social.md", "qa-checklist.md", "licensing.md", "changelog.md")


def _expand(h):
    h = h.upper()
    return "#" + "".join(c * 2 for c in h[1:]) if len(h) == 4 else h


def palette(ir):
    return {hx.upper() for _t, _r, _n, hx, _u in colors(ir)}


def unapproved_colors(text, pal):
    return sorted({m.group(0) for m in HEX_ANY.finditer(text) if _expand(m.group(0)) not in pal})


def check(name, ok, detail, warn=False):
    return {"check": name, "result": "PASS" if ok else ("WARNING" if warn else "FAIL"), "detail": detail}


def brand_qa(ir, skill_dir=None, portable_dir=None, preview_dir=None):
    out = []
    rows = contrast_table(ir)
    core_fail = [r["name"] for r in rows if r["result"] == "FAIL" and r.get("core")]
    out.append(check("a11y.core_pairs", not core_fail, {"failing": core_fail, "pairs": len(rows)}))
    other_fail = [r["name"] for r in rows if r["result"] == "FAIL" and not r.get("core")]
    out.append(check("a11y.non_core_pairs", not other_fail, {"failing": other_fail}, warn=True))
    out.append(check("rules.no_contradiction", not rule_contradictions(ir["rules"]), rule_contradictions(ir["rules"])))
    pal = palette(ir)
    fams = ir["design_system"]["typography"]["families"]
    out.append(check("fonts.fallback_generic_last", all(f["fallbacks"] and f["fallbacks"][-1] in ("sans-serif", "serif") for f in fams),
                     [f["role"] for f in fams]))
    bad_assets = [a["id"] for a in ir["assets"] if a["include"] and not a["redistribution_allowed"]]
    out.append(check("license.assets_included_only_if_allowed", not bad_assets, bad_assets))
    out.append(check("license.fonts_not_bundled", not any(f["bundled"] for f in ir["fonts"]), [f["family"] for f in ir["fonts"] if f["bundled"]]))

    primary = next(hx for _t, r, _n, hx, _u in colors(ir) if r == "primary")
    if preview_dir:
        for f in sorted(Path(preview_dir).glob("*.html")):
            text = f.read_text(encoding="utf-8")
            out.append(check("preview.%s.approved_colors_only" % f.name, not unapproved_colors(text, pal), unapproved_colors(text, pal)))
            out.append(check("preview.%s.offline" % f.name, not EXTERNAL.search(text), "external reference found" if EXTERNAL.search(text) else "ok"))
            out.append(check("preview.%s.no_script" % f.name, "<script" not in text.lower(), "ok"))
            out.append(check("preview.%s.accent_not_text" % f.name,
                             not re.search(r"(?<![-\w])color\s*:\s*var\(--color-accent\)", text), "ok"))
    if skill_dir:
        sk = Path(skill_dir)
        missing = [r for r in REQUIRED_REFS if not (sk / "references" / r).is_file()]
        out.append(check("skill.required_references", not missing, missing))
        fonts_in_pkg = [p.name for p in sk.rglob("*") if p.suffix.lower() in FONT_EXT]
        out.append(check("skill.no_font_files", not fonts_in_pkg, fonts_in_pkg))
        tj = json.loads((sk / "templates/tokens.json").read_text(encoding="utf-8"))
        css = (sk / "templates/tokens.css").read_text(encoding="utf-8")
        cmd = (sk / "references/color.md").read_text(encoding="utf-8")
        same = [tj["color"]["primary"]["$value"].upper() == primary.upper(), ("--color-primary: %s;" % primary) in css, primary in cmd]
        if portable_dir:
            same.append(primary in (Path(portable_dir) / "DESIGN.md").read_text(encoding="utf-8"))
        if preview_dir:
            same.append(primary in (Path(preview_dir) / "poster.html").read_text(encoding="utf-8"))
        out.append(check("sot.primary_consistent", all(same), {"primary": primary, "checks": same}))
        unapproved_css = unapproved_colors(css, pal)
        out.append(check("skill.tokens_css_palette_only", not unapproved_css, unapproved_css))
    return out


def summarize(results):
    fails = [r for r in results if r["result"] == "FAIL"]
    warns = [r for r in results if r["result"] == "WARNING"]
    return {"passed": not fails, "fail": len(fails), "warning": len(warns), "total": len(results)}
