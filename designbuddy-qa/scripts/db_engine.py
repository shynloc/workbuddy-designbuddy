"""Intake (existing / partial / new), design-system generation and Design Gates.

Everything here is deterministic: the same brief + decisions give the same IR.
"""
import json

import db_color as C
from db_ir import GATES, fact, is_fact, iter_facts, contrast_table
from db_util import (DBError, DESIGNBUDDY_VERSION, SCHEMA_VERSION, SLUG_RE, TEMPLATES,
                   now_iso, safe_font_name, safe_radius, safe_relpath, safe_text, safe_weight)

BRIEF_VERSION = "1.0.0"
COLOR_ROLES = {
    "primary": ("color.primary", "主色", "标题强调、按钮、图表主序列"),
    "ink": ("color.ink", "正文墨色", "正文与标题文字"),
    "paper": ("color.paper", "页面底色", "页面与幻灯片背景"),
    "surface": ("color.surface", "浅色面", "卡片、分区背景"),
    "accent": ("color.accent", "强调色", "少量高亮与数据标注（非正文文字）"),
    "on-primary": ("color.on-primary", "主色上的文字", "主色填充上的文字与图标"),
    "brand-text": ("color.brand-text", "品牌色文字", "需要品牌色的文字与链接"),
    "success": ("color.success", "成功", "成功状态"),
    "warning": ("color.warning", "警告", "警告状态"),
    "error": ("color.error", "错误", "错误状态"),
    "info": ("color.info", "信息", "提示信息"),
}
SEMANTIC_SEEDS = {"success": "#15803D", "warning": "#B45309", "error": "#B91C1C", "info": "#1D4ED8"}
TYPE_SCALE = [
    ("display", 56, 1.15), ("h1", 40, 1.2), ("h2", 28, 1.3), ("h3", 22, 1.35),
    ("body", 16, 1.7), ("small", 14, 1.6), ("caption", 12, 1.5),
]
PATCHABLE = {"G1": ("brand.",), "G2": ("direction",), "G3": ("color.", "font.", "heading_weight", "radius", "resolve.", "override."),
             "G4": ("app.",), "G5": (), "G6": ()}


def _load_data(name):
    return json.loads((TEMPLATES / ("data." + name)).read_text(encoding="utf-8"))


def directions():
    return _load_data("directions.json")["directions"]


def font_kb():
    return _load_data("fonts.json")


def rank_directions(keywords):
    kws = [k.lower() for k in keywords]
    scored = []
    for i, d in enumerate(directions()):
        score = sum(1 for k in kws for dk in d["keywords"] if dk.lower() in k or k in dk.lower())
        scored.append((-score, i, d))
    scored.sort()
    return [dict(d, match_score=-s) for s, _i, d in scored]


# ---------------------------------------------------------------- intake

def load_brief(brief):
    if not isinstance(brief, dict):
        raise DBError("E_BRIEF", "brief 必须是 JSON 对象")
    if brief.get("brief_version") != BRIEF_VERSION:
        raise DBError("E_BRIEF_VERSION", "brief_version 必须为 %s" % BRIEF_VERSION)
    path = brief.get("path")
    if path not in ("existing", "partial", "new"):
        raise DBError("E_BRIEF", "path 必须是 existing / partial / new")
    b = brief.get("brand") or {}
    slug = b.get("slug")
    if not isinstance(slug, str) or not SLUG_RE.match(slug) or len(slug) > 48:
        raise DBError("E_SLUG", "brand.slug 只能包含小写字母、数字和连字符（≤48）：%r" % slug)
    safe_text(b.get("name"), "brand.name", 60)
    for a in b.get("aliases", []):
        safe_text(a, "brand.aliases", 60)
    for i, a in enumerate(brief.get("assets", [])):
        safe_relpath(a.get("file"), "assets[%d].file" % i)
    return brief


def _brand_section(brief):
    b = brief["brand"]
    src = "DOCUMENTED" if brief["path"] == "existing" else "USER_CONFIRMED"
    names = [b["name"]] + [x for x in (b.get("name_zh"), b.get("name_en")) if x]
    aliases = []
    for a in names + list(b.get("aliases", [])):
        a = safe_text(a, "alias", 60)
        if a.lower() not in [x.lower() for x in aliases]:
            aliases.append(a)
    sec = {
        "name": fact(safe_text(b["name"], "brand.name", 60), src),
        "name_zh": fact(b.get("name_zh") or b["name"], src),
        "name_en": fact(b.get("name_en") or b["name"], src),
        "slug": b["slug"],
        "aliases": fact(aliases, src),
        "industry": fact(safe_text(b.get("industry", "未提供"), "brand.industry"), src if b.get("industry") else "INFERRED", "high" if b.get("industry") else "low"),
        "audience": fact(safe_text(b.get("audience", "未提供"), "brand.audience"), src if b.get("audience") else "INFERRED", "high" if b.get("audience") else "low"),
        "positioning": fact(safe_text(b.get("positioning", "未提供"), "brand.positioning", 300), src if b.get("positioning") else "INFERRED", "high" if b.get("positioning") else "low"),
        "personality": fact(list(b.get("personality", [])), src if b.get("personality") else "INFERRED", "high" if b.get("personality") else "low"),
        "values": fact(list(b.get("values", [])), src),
        "anti_personality": fact(list(b.get("anti_personality", [])), src),
        "voice": {
            "tone": fact((brief.get("voice") or {}).get("tone", ""), src) if (brief.get("voice") or {}).get("tone") else None,
            "preferred_language": fact((brief.get("voice") or {}).get("preferred", []), src),
            "avoid_language": fact((brief.get("voice") or {}).get("avoid", []), src),
        },
        "identity": {"logo_asset": None, "clear_space": fact("Logo 高度的 50%", "GENERATED", "medium"),
                     "minimum_size": fact("屏幕 24px / 印刷 8mm", "GENERATED", "medium")},
    }
    for a in brief.get("assets", []):
        if a.get("type") == "logo":
            sec["identity"]["logo_asset"] = a["id"]
            break
    return sec


def _resolve_known(brief, field_path, validator):
    """Return (value, fact_kwargs, conflict) from brief.known.* observations."""
    node = brief.get("known") or {}
    for k in field_path.split("."):
        node = node.get(k) if isinstance(node, dict) else None
    if node is None:
        return None, None, None
    obs = node if isinstance(node, list) else [node]
    vals = []
    for o in obs:
        v, s = (o.get("value"), o.get("source")) if isinstance(o, dict) else (o, None)
        vals.append((validator(v, field_path), s))
    distinct = []
    for v, _s in vals:
        if v not in distinct:
            distinct.append(v)
    src_type = "DOCUMENTED" if any(s for _v, s in vals) else "USER_CONFIRMED"
    evidence = ["source:%s" % s for _v, s in vals if s]
    if len(distinct) > 1:
        counts = sorted(distinct, key=lambda v: -sum(1 for x, _ in vals if x == v))
        conflict = {"id": "conflict-" + field_path.replace(".", "-"), "field": field_path,
                    "candidates": [{"value": v, "sources": [s for x, s in vals if x == v and s]} for v in counts],
                    "suggested": counts[0], "status": "open"}
        return counts[0], dict(source_type=src_type, confidence="low", evidence=evidence, review="pending"), conflict
    review = "approved" if src_type == "USER_CONFIRMED" else "pending"
    return distinct[0], dict(source_type=src_type, confidence="high", evidence=evidence, review=review), None


def _color_validator(v, field):
    return C.norm_hex(v, field)


def _text_validator(v, field):
    return safe_font_name(v, field)


def build_design_system(brief, direction, conflicts):
    """Known values are preserved; every gap is GENERATED from the direction."""
    ev_dir = ["direction:%s" % direction["id"]]
    colors = {}

    def take(role, generator):
        val, meta, conflict = _resolve_known(brief, "colors.%s" % role, _color_validator)
        if conflict:
            conflicts.append(conflict)
        if val is not None:
            colors[role] = fact(val, **meta)
        else:
            colors[role] = fact(generator(), "GENERATED", "medium", ev_dir)

    take("primary", lambda: direction["seed_primary"])
    p = colors["primary"]["value"]
    take("paper", lambda: "#FFFFFF")
    take("ink", lambda: C.neutral_ink(p))
    take("surface", lambda: C.neutral_surface(p))
    take("accent", lambda: C.darken_until(C.tint(_rotate(p), 0.45), colors["paper"]["value"], 3.0))
    paper = colors["paper"]["value"]
    colors["on-primary"] = fact(C.best_on(p, paper if C.luminance(paper) > 0.5 else "#FFFFFF", colors["ink"]["value"]),
                                "GENERATED", "high", ["derived:contrast(color.primary)"])
    if C.contrast(p, paper) >= 4.5:
        colors["brand-text"] = fact(p, "GENERATED", "high", ["derived:=color.primary"])
    else:
        colors["brand-text"] = fact(C.darken_until(p, paper, 4.5), "GENERATED", "high", ["derived:darken(color.primary)>=4.5"])
    for role, seed in SEMANTIC_SEEDS.items():
        take(role, lambda seed=seed: C.darken_until(seed, paper, 4.5))

    color_list = []
    for role, (token, name, usage) in COLOR_ROLES.items():
        color_list.append({"token": token, "role": role, "name": name, "usage": usage, "hex": colors[role]})

    kb = font_kb()
    fams = []
    for role, key in (("heading", "heading_font"), ("body", "body_font")):
        val, meta, conflict = _resolve_known(brief, "fonts.%s" % role, _text_validator)
        if conflict:
            conflicts.append(conflict)
        f = fact(val, **meta) if val is not None else fact(direction[key], "GENERATED", "medium", ev_dir)
        info = kb["families"].get(f["value"])
        category = info["category"] if info else "sans-serif"
        fallbacks = [x for x in kb["fallbacks"][category] if x != f["value"]]
        fams.append({"role": role, "family": f, "category": category, "fallbacks": fallbacks})
    hw_raw = (brief.get("known") or {}).get("heading_weight")
    heading_weight = fact(safe_weight(hw_raw), "USER_CONFIRMED") if hw_raw is not None else fact(direction["heading_weight"], "GENERATED", "medium", ev_dir)
    radius_raw = (brief.get("known") or {}).get("radius")
    radius = fact(safe_radius(radius_raw), "USER_CONFIRMED") if radius_raw else fact(direction["radius"], "GENERATED", "medium", ev_dir)
    base = direction["spacing_base"]

    pairs = [
        {"name": "body-text/page", "fg": "color.ink", "bg": "color.paper", "kind": "text", "core": True},
        {"name": "body-text/surface", "fg": "color.ink", "bg": "color.surface", "kind": "text", "core": True},
        {"name": "on-primary/primary", "fg": "color.on-primary", "bg": "color.primary", "kind": "text", "core": True},
        {"name": "brand-text/page", "fg": "color.brand-text", "bg": "color.paper", "kind": "text", "core": True},
        {"name": "primary-as-text/page", "fg": "color.primary", "bg": "color.paper", "kind": "large", "core": False},
        {"name": "accent-ui/page", "fg": "color.accent", "bg": "color.paper", "kind": "ui", "core": False},
    ] + [{"name": "%s/page" % r, "fg": "color.%s" % r, "bg": "color.paper", "kind": "text", "core": True}
         for r in SEMANTIC_SEEDS]

    return {
        "direction": {"id": direction["id"], "name_zh": direction["name_zh"], "name_en": direction["name_en"]},
        "colors": color_list,
        "typography": {
            "families": fams,
            "heading_weight": heading_weight,
            "body_weight": 400,
            "scale": [{"token": t, "size_px": s, "line_height": lh} for t, s, lh in TYPE_SCALE],
            "slide_scale": {"title": 40, "subtitle": 28, "body": 18, "note": 12},
            "cjk": "中英文之间留半角空格；标点使用全角；正文两端对齐时避免孤字",
        },
        "spacing": {"base": base, "scale": [base * n for n in (1, 2, 3, 4, 6, 8, 12, 16)]},
        "radius": radius,
        "shadows": {"sm": "0 1px 2px rgba(0,0,0,.08)", "md": "0 4px 16px rgba(0,0,0,.10)"},
        "grid": {"web": "12 栏，栏间距 24px，最大宽度 1200px", "slide": "16:9，左右边距 64px", "print": "A4，页边距 20mm"},
        "layout": fact(direction["layout"], "GENERATED", "medium", ev_dir),
        "imagery": fact(direction["imagery"], "GENERATED", "medium", ev_dir),
        "iconography": fact(direction["iconography"], "GENERATED", "medium", ev_dir),
        "motion": fact(direction["motion"], "GENERATED", "medium", ev_dir),
        "accessibility": {"target": "WCAG 2.x AA", "pairs": pairs, "overrides": []},
    }


def _rotate(hex_color, turn=0.45):
    import colorsys
    r, g, b = (v / 255.0 for v in C.rgb(hex_color))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    r2, g2, b2 = colorsys.hls_to_rgb((h + turn) % 1.0, l, max(s, 0.55))
    return C.to_hex(r2 * 255, g2 * 255, b2 * 255)


def build_applications(direction):
    ev = ["direction:%s" % direction["id"]]
    g = lambda text: fact(text, "GENERATED", "medium", ev)  # noqa: E731
    return {
        "presentation": [g(direction["ppt"]), g("16:9；标题字号 40、正文 18；图表主序列用 color.primary，其余用中性灰")],
        "document": [g("Word / PDF：标题使用 heading 字体，正文 body 字体 11–12pt，行距 1.5"), g("页眉放置 Logo（遵守安全区），页脚放页码")],
        "spreadsheet": [g("Excel：表头填充 color.primary + color.on-primary 文字；数据行交替使用 color.paper / color.surface"), g("数字右对齐，千分位；负数用 color.error")],
        "web": [g(direction["layout"]), g("按钮：color.primary 填充，圆角使用 radius token；链接使用 color.brand-text")],
        "poster": [g(direction["poster"]), g("文字压图时加 color.ink 60% 遮罩，确保对比度")],
        "social": [g("小红书 1242×1660、公众号封面 900×383、竖版 1080×1920；Logo 置于安全区内"), g(direction["imagery"])],
    }


def build_rules(brief, ds):
    acc = next(c for c in ds["colors"] if c["role"] == "accent")["hex"]["value"]
    paper = next(c for c in ds["colors"] if c["role"] == "paper")["hex"]["value"]
    prim = next(c for c in ds["colors"] if c["role"] == "primary")["hex"]["value"]
    fams = {f["role"]: f["family"]["value"] for f in ds["typography"]["families"]}

    def rule(rid, text, subject=None, action=None, src="GENERATED", review="pending"):
        return {"id": rid, "level": rid.split("-")[0], "text_zh": text, "subject": subject, "action": action,
                "source_type": src, "confidence": "high" if src != "GENERATED" else "medium", "review": review}

    rules = [
        rule("MUST-COLOR-01", "主色固定为 %s（color.primary）" % prim, "color.primary", "use_as_brand_color"),
        rule("MUST-TYPE-01", "所有一级标题使用 %s，字重 %s" % (fams["heading"], ds["typography"]["heading_weight"]["value"]), "font.heading", "use_for_headings"),
        rule("MUST-TYPE-02", "正文使用 %s；不可用时按回退栈替换" % fams["body"], "font.body", "use_for_body"),
        rule("MUST-A11Y-01", "正文文字与背景对比度不低于 4.5:1，大字号不低于 3:1", "a11y", "contrast"),
        rule("NEVER-LOGO-01", "不得拉伸、旋转、变色 Logo，不得为 Logo 添加阴影或描边", "logo", "distort"),
        rule("NEVER-COLOR-01", "不得使用色板以外的颜色（照片与插画内容除外）", "palette", "use_unlisted"),
        rule("AVOID-COLOR-01", "强调色 color.accent 大面积用作背景", "color.accent", "use_as_large_background"),
        rule("SHOULD-LAYOUT-01", "间距使用 spacing 刻度（%s 的倍数）" % ds["spacing"]["base"], "spacing", "use_scale"),
    ]
    if C.contrast(acc, paper) < 4.5:
        rules.append(rule("NEVER-COLOR-02", "强调色 color.accent 不得用作正文或标题文字", "color.accent", "use_as_text"))
    if C.contrast(prim, paper) < 4.5:
        rules.append(rule("NEVER-COLOR-03", "主色不得直接用作小号文字，需要品牌色文字时使用 color.brand-text", "color.primary", "use_as_small_text"))
    for r in (brief.get("known") or {}).get("rules", []):
        rid = r.get("id", "")
        rules.append({"id": rid, "level": r.get("level", rid.split("-")[0] if isinstance(rid, str) else ""),
                      "text_zh": r.get("text", ""), "subject": r.get("subject"), "action": r.get("action"),
                      "source_type": "DOCUMENTED", "confidence": "high", "review": "pending"})
    return rules


def _assets(brief):
    out = []
    for a in brief.get("assets", []):
        redistribution = a.get("redistribution_allowed") is True
        out.append({"id": a.get("id"), "file": safe_relpath(a.get("file"), "asset.file"), "type": a.get("type", "other"),
                    "owner": a.get("owner", "unknown"), "license": a.get("license", "unknown"),
                    "redistribution_allowed": redistribution,
                    "include": bool(redistribution and a.get("license") not in (None, "", "unknown")),
                    "notes": a.get("notes", "")})
    return out


def _fonts(ds):
    kb = font_kb()
    out = []
    for f in ds["typography"]["families"]:
        fam = f["family"]["value"]
        info = kb["families"].get(fam)
        out.append({"family": fam, "role": f["role"], "weights": [400, ds["typography"]["heading_weight"]["value"]],
                    "source": "font-kb" if info else "user",
                    "license": info["license"] if info else "UNKNOWN — 需用户确认",
                    "license_url": info["license_url"] if info else "",
                    "redistribution_allowed": bool(info and info["redistribution_allowed"] is True),
                    "bundled": False, "fallbacks": f["fallbacks"], "verified_at": kb["verified_at"] if info else None})
    return out


def intake(brief):
    brief = load_brief(brief)
    path = brief["path"]
    keywords = list((brief.get("discovery") or {}).get("keywords", [])) + list(brief["brand"].get("personality", []))
    ranked = rank_directions(keywords)
    conflicts = []
    ir = {
        "schema_version": SCHEMA_VERSION,
        "metadata": {"system_version": "1.0.0", "generated_by": "DesignBuddy %s" % DESIGNBUDDY_VERSION,
                     "path": path, "created_at": now_iso(), "locale": ["zh-CN", "en"]},
        "brand": _brand_section(brief),
        "design_system": None,
        "applications": None,
        "rules": [],
        "conflicts": [],
        "candidates": [{"id": d["id"], "name_zh": d["name_zh"], "name_en": d["name_en"], "match_score": d["match_score"],
                        "seed_primary": d["seed_primary"], "heading_font": d["heading_font"], "voice_tone": d["voice_tone"]}
                       for d in ranked[:3]],
        "assets": _assets(brief),
        "fonts": [],
        "sources": [dict(s, included_in_final=False) for s in brief.get("sources", [])],
        "gates": {g: {"status": "NOT_STARTED", "rounds": 0} for g in GATES},
        "version": {"system": "1.0.0", "skill": "1.0.0", "changelog": [{"version": "1.0.0", "note": "初始版本"}]},
    }
    ir["gates"]["G1"]["status"] = "IN_REVIEW"
    if path in ("existing", "partial"):
        _materialise(ir, brief, ranked[0], conflicts)
    return ir


def _materialise(ir, brief, direction, conflicts):
    ds = build_design_system(brief, direction, conflicts)
    ir["design_system"] = ds
    ir["applications"] = build_applications(direction)
    ir["rules"] = build_rules(brief, ds)
    ir["fonts"] = _fonts(ds)
    ir["conflicts"] = conflicts
    tone = ir["brand"]["voice"].get("tone")
    if tone is None:
        ir["brand"]["voice"]["tone"] = fact(direction["voice_tone"], "GENERATED", "medium", ["direction:%s" % direction["id"]])


# ---------------------------------------------------------------- gates

def _approve(node, gate):
    for _ptr, f in iter_facts(node):
        if f["review"] == "pending":
            f["review"] = "approved"
            f.setdefault("approved_at", gate)


def apply_gate(ir, brief, gate, decision, patch=None, note=""):
    """Apply KEEP / CHANGE / REJECT to a gate. Returns a review record."""
    if gate not in GATES:
        raise DBError("E_GATE", "未知 Gate：%s" % gate)
    if decision not in ("KEEP", "CHANGE", "REJECT"):
        raise DBError("E_GATE", "decision 只能是 KEEP / CHANGE / REJECT")
    idx = GATES.index(gate)
    if idx > 0 and ir["gates"][GATES[idx - 1]]["status"] != "KEEP":
        raise DBError("E_GATE_ORDER", "必须先确认 %s，才能进行 %s" % (GATES[idx - 1], gate))
    patch = patch or {}
    allowed = PATCHABLE[gate]
    for k in patch:
        if not any(k == a or k.startswith(a) for a in allowed):
            raise DBError("E_PATCH", "%s 不允许修改字段 %s" % (gate, k))
    g = ir["gates"][gate]
    record = {"gate": gate, "decision": decision, "patch": patch, "note": note, "at": now_iso()}

    if decision == "REJECT":
        g["status"] = "REJECTED"
        if idx > 0:
            ir["gates"][GATES[idx - 1]]["status"] = "IN_REVIEW"
        return record

    if decision == "CHANGE":
        g["rounds"] = g.get("rounds", 0) + 1
        g["status"] = "IN_REVIEW"
        _apply_patch(ir, brief, gate, patch)
        if g["rounds"] >= 3:
            record["advice"] = "同一 Gate 已修改 3 轮：请提供 A/B 两个具体方案让用户二选一"
        return record

    # KEEP
    if gate == "G2" and ir["design_system"] is None:
        chosen = patch.get("direction") or (ir["candidates"][0]["id"] if ir["candidates"] else None)
        _apply_patch(ir, brief, "G2", {"direction": chosen})
    if gate == "G1":
        _approve(ir["brand"], gate)
    elif gate == "G3":
        if ir["design_system"] is None:
            raise DBError("E_GATE", "尚未生成设计系统")
        open_conflicts = [c["id"] for c in ir.get("conflicts", []) if c["status"] == "open"]
        if open_conflicts:
            raise DBError("E_GATE_BLOCKED", "仍有未裁决的冲突：%s" % ", ".join(open_conflicts))
        failing = [r for r in contrast_table(ir) if r["result"] == "FAIL" and r.get("core")]
        if failing:
            raise DBError("E_GATE_BLOCKED", "核心配色对比度不达标：%s" % ", ".join(
                "%s %.2f:1" % (r["name"], r["ratio"]) for r in failing),
                {"pairs": [r["name"] for r in failing]})
        _approve(ir["design_system"], gate)
        _approve(ir["fonts"], gate)
        _approve(ir["brand"]["voice"], gate)  # New 路径的语气在 G2 才生成，随核心系统一起确认
    elif gate == "G4":
        _approve(ir["applications"], gate)
        for r in ir["rules"]:
            if r["review"] == "pending":
                r["review"] = "approved"
    elif gate == "G5":
        if not (ir.get("metadata", {}).get("preview") or {}).get("qa_passed"):
            raise DBError("E_GATE_BLOCKED", "需要先生成 Preview 且 QA 无 FAIL")
    g["status"] = "KEEP"
    if idx + 1 < len(GATES) and ir["gates"][GATES[idx + 1]]["status"] == "NOT_STARTED":
        ir["gates"][GATES[idx + 1]]["status"] = "IN_REVIEW"
    return record


def _set_color(ir, role, hexv):
    for c in ir["design_system"]["colors"]:
        if c["role"] == role:
            c["hex"] = fact(C.norm_hex(hexv, "color.%s" % role), "USER_CONFIRMED", review="changed")
            return
    raise DBError("E_PATCH", "没有这个颜色角色：%s" % role)


def _apply_patch(ir, brief, gate, patch):
    for k, v in patch.items():
        if k == "direction":
            d = next((x for x in directions() if x["id"] == v), None)
            if not d:
                raise DBError("E_PATCH", "未知视觉方向：%s" % v)
            conflicts = []
            _materialise(ir, brief, d, conflicts)
            ir["metadata"]["direction"] = d["id"]
        elif k.startswith("brand."):
            field = k.split(".", 1)[1]
            if field not in ("industry", "audience", "positioning"):
                raise DBError("E_PATCH", "不能修改 %s" % k)
            ir["brand"][field] = fact(safe_text(v, k, 300), "USER_CONFIRMED", review="changed")
        elif k.startswith("color."):
            _set_color(ir, k.split(".", 1)[1], v)
        elif k.startswith("font."):
            role = k.split(".", 1)[1]
            for f in ir["design_system"]["typography"]["families"]:
                if f["role"] == role:
                    f["family"] = fact(safe_font_name(v, k), "USER_CONFIRMED", review="changed")
            ir["fonts"] = _fonts(ir["design_system"])
        elif k == "heading_weight":
            ir["design_system"]["typography"]["heading_weight"] = fact(safe_weight(v), "USER_CONFIRMED", review="changed")
        elif k == "radius":
            ir["design_system"]["radius"] = fact(safe_radius(v), "USER_CONFIRMED", review="changed")
        elif k.startswith("resolve."):
            cid = k.split(".", 1)[1]
            c = next((x for x in ir.get("conflicts", []) if x["id"] == cid), None)
            if not c:
                raise DBError("E_PATCH", "没有这个冲突：%s" % cid)
            field = c["field"]
            if field.startswith("colors."):
                _set_color(ir, field.split(".", 1)[1], v)
            elif field.startswith("fonts."):
                _apply_patch(ir, brief, gate, {"font.%s" % field.split(".", 1)[1]: v})
            c["status"] = "resolved"
            c["resolution"] = v
        elif k.startswith("override."):
            pair = k.split(".", 1)[1]
            ir["design_system"]["accessibility"]["overrides"].append(
                {"pair": pair, "reason": safe_text(v, k, 200), "source_type": "USER_CONFIRMED", "review": "user_override"})
            for p in ir["design_system"]["accessibility"]["pairs"]:
                if p["name"] == pair:
                    p["core"] = False
        if k.startswith(("color.", "font.", "resolve.", "radius", "heading_weight")) and ir.get("design_system"):
            ir["rules"] = build_rules(brief, ir["design_system"])


def provenance_summary(ir):
    counts, low, pending = {}, [], []
    for ptr, f in iter_facts(ir):
        counts[f["source_type"]] = counts.get(f["source_type"], 0) + 1
        if f["confidence"] == "low":
            low.append(ptr)
        if f["review"] == "pending":
            pending.append(ptr)
    return {"counts": counts, "low_confidence": low, "pending": pending,
            "review_first": [p for p, f in iter_facts(ir) if f["source_type"] in ("INFERRED", "GENERATED") and f["review"] == "pending"]}
