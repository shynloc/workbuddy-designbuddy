"""Brand IR data model helpers and validator.

Brand IR is the single machine-readable source of truth (JSON). This module
implements the checks DesignBuddy needs (required fields, types, enums,
cross references, business rules). It is NOT a general JSON Schema validator.
"""
from . import color as C
from .util import (DBError, HEX_RE, RULE_ID_RE, SCHEMA_VERSION, SLUG_RE,
                   CONTROL_RE, safe_relpath)

SOURCE_TYPES = ("USER_CONFIRMED", "DOCUMENTED", "EXTRACTED", "INFERRED", "GENERATED")
CONFIDENCE = ("high", "medium", "low")
REVIEW = ("pending", "approved", "changed", "rejected", "user_override")
LEVELS = ("MUST", "SHOULD", "AVOID", "NEVER")
GATES = ("G1", "G2", "G3", "G4", "G5", "G6")
GATE_STATUS = ("NOT_STARTED", "IN_REVIEW", "KEEP", "REJECTED")
PATHS = ("existing", "partial", "new")
CORE_PAIRS = ("body-text/page", "on-primary/primary", "brand-text/page")


def fact(value, source_type, confidence="high", evidence=None, review=None):
    if review is None:
        review = "approved" if source_type in ("USER_CONFIRMED",) else "pending"
    return {"value": value, "source_type": source_type, "confidence": confidence,
            "review": review, "evidence": list(evidence or [])}


def is_fact(x):
    return isinstance(x, dict) and "value" in x and "source_type" in x


def iter_facts(node, path=""):
    """Yield (json_pointer, fact) for every Fact in the IR."""
    if is_fact(node):
        yield path, node
        return
    if isinstance(node, dict):
        for k, v in node.items():
            yield from iter_facts(v, "%s/%s" % (path, k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from iter_facts(v, "%s/%d" % (path, i))


def color_map(ir):
    """token -> hex for every colour token."""
    ds = ir.get("design_system") or {}
    return {c["token"]: c["hex"]["value"] for c in ds.get("colors", [])}


def contrast_table(ir):
    cmap = color_map(ir)
    ds = ir.get("design_system") or {}
    overrides = {o["pair"]: o for o in ds.get("accessibility", {}).get("overrides", [])}
    rows = []
    for p in ds.get("accessibility", {}).get("pairs", []):
        fg, bg = cmap.get(p["fg"]), cmap.get(p["bg"])
        if fg is None or bg is None:
            rows.append(dict(p, ratio=None, result="FAIL", note="token missing"))
            continue
        r = C.contrast(fg, bg)
        res = C.grade(r, p.get("kind", "text"))
        row = dict(p, fg_hex=fg, bg_hex=bg, ratio=round(r, 2), result=res)
        if res == "FAIL" and p["name"] in overrides:
            row["result"] = "USER_OVERRIDE"
            row["override_reason"] = overrides[p["name"]].get("reason", "")
        rows.append(row)
    return rows


def rule_contradictions(rules):
    """MUST vs NEVER/AVOID on the same (subject, action) is a contradiction."""
    seen = {}
    out = []
    for r in rules:
        key = (r.get("subject"), r.get("action"))
        if not key[0] or not key[1]:
            continue
        seen.setdefault(key, []).append(r)
    for key, rs in seen.items():
        levels = {r["level"] for r in rs}
        if "MUST" in levels and (levels & {"NEVER", "AVOID"}):
            out.append({"subject": key[0], "action": key[1], "rules": sorted(r["id"] for r in rs)})
    return out


def _err(errors, code, msg, where=""):
    errors.append({"code": code, "message": msg, "where": where})


def validate(ir, stage="draft"):
    """Return {"errors": [...], "warnings": [...], "pending": [...]}.

    stage: "draft" (structure only) or "release" (also gates, review, a11y).
    """
    errors, warnings, pending = [], [], []
    if not isinstance(ir, dict):
        return {"errors": [{"code": "E_TYPE", "message": "Brand IR 必须是 JSON 对象", "where": "/"}],
                "warnings": [], "pending": []}

    sv = ir.get("schema_version")
    if sv != SCHEMA_VERSION:
        _err(errors, "E_SCHEMA_VERSION", "schema_version 必须为 %s，实际为 %r" % (SCHEMA_VERSION, sv), "/schema_version")

    meta = ir.get("metadata") or {}
    if meta.get("path") not in PATHS:
        _err(errors, "E_ENUM", "metadata.path 必须是 existing/partial/new", "/metadata/path")
    for k in ("system_version", "generated_by"):
        if not meta.get(k):
            _err(errors, "E_REQUIRED", "缺少 metadata.%s" % k, "/metadata/%s" % k)

    brand = ir.get("brand") or {}
    slug = brand.get("slug")
    if not isinstance(slug, str) or not SLUG_RE.match(slug or "") or len(slug) > 48:
        _err(errors, "E_SLUG", "brand.slug 只能包含小写字母、数字和连字符：%r" % slug, "/brand/slug")
    for k in ("name", "industry", "audience", "positioning"):
        f = brand.get(k)
        if not is_fact(f):
            _err(errors, "E_REQUIRED", "缺少 brand.%s" % k, "/brand/%s" % k)
        elif not isinstance(f["value"], str) or CONTROL_RE.search(f["value"]):
            _err(errors, "E_FIELD", "brand.%s 必须是单行文本" % k, "/brand/%s" % k)
    aliases = brand.get("aliases", {}).get("value", []) if is_fact(brand.get("aliases")) else []
    if len(set(a.lower() for a in aliases)) != len(aliases):
        _err(errors, "E_DUPLICATE", "brand.aliases 存在重复项", "/brand/aliases")

    for ptr, f in iter_facts(ir):
        if f.get("source_type") not in SOURCE_TYPES:
            _err(errors, "E_PROVENANCE", "source_type 非法：%r" % f.get("source_type"), ptr)
        if f.get("confidence") not in CONFIDENCE:
            _err(errors, "E_PROVENANCE", "confidence 非法：%r" % f.get("confidence"), ptr)
        if f.get("review") not in REVIEW:
            _err(errors, "E_PROVENANCE", "review 非法：%r" % f.get("review"), ptr)
        if f.get("review") == "pending":
            pending.append(ptr)

    ds = ir.get("design_system")
    if ds is None:
        if meta.get("path") != "new" or stage == "release":
            _err(errors, "E_REQUIRED", "缺少 design_system", "/design_system")
    else:
        tokens = [c.get("token") for c in ds.get("colors", [])]
        if len(set(tokens)) != len(tokens):
            _err(errors, "E_DUPLICATE", "颜色 token 重复", "/design_system/colors")
        for i, c in enumerate(ds.get("colors", [])):
            hx = c.get("hex", {}).get("value") if is_fact(c.get("hex")) else None
            if not isinstance(hx, str) or not HEX_RE.match(hx):
                _err(errors, "E_COLOR", "颜色值非法：%r" % hx, "/design_system/colors/%d" % i)
        for need in ("color.primary", "color.ink", "color.paper", "color.on-primary"):
            if need not in tokens:
                _err(errors, "E_REQUIRED", "缺少颜色 token %s" % need, "/design_system/colors")
        fams = ds.get("typography", {}).get("families", [])
        roles = [f.get("role") for f in fams]
        for need in ("heading", "body"):
            if need not in roles:
                _err(errors, "E_REQUIRED", "缺少 %s 字体" % need, "/design_system/typography")
        for i, f in enumerate(fams):
            fb = f.get("fallbacks") or []
            if not fb or fb[-1] not in ("sans-serif", "serif", "monospace"):
                _err(errors, "E_FONT_FALLBACK", "字体 %s 缺少以通用字族结尾的回退栈" % f.get("role"),
                     "/design_system/typography/families/%d" % i)
        if stage == "release":
            for row in contrast_table(ir):
                if row["result"] == "FAIL" and (row["name"] in CORE_PAIRS or row.get("core")):
                    _err(errors, "E_A11Y", "核心配色对比度不达标：%s %.2f:1" % (row["name"], row["ratio"] or 0),
                         "/design_system/accessibility")
                elif row["result"] in ("FAIL", "WARNING"):
                    warnings.append({"code": "W_A11Y", "message": "%s %s %.2f:1" % (row["name"], row["result"], row["ratio"] or 0)})

    rules = ir.get("rules", [])
    ids = [r.get("id") for r in rules]
    if len(set(ids)) != len(ids):
        dup = sorted({i for i in ids if ids.count(i) > 1})
        _err(errors, "E_DUPLICATE_RULE", "规则 ID 重复：%s" % ", ".join(map(str, dup)), "/rules")
    for i, r in enumerate(rules):
        rid = r.get("id", "")
        if not isinstance(rid, str) or not RULE_ID_RE.match(rid):
            _err(errors, "E_RULE_ID", "规则 ID 格式错误：%r" % rid, "/rules/%d" % i)
        elif r.get("level") != rid.split("-")[0]:
            _err(errors, "E_RULE_LEVEL", "规则 %s 的 level 与 ID 前缀不一致" % rid, "/rules/%d" % i)
        if not r.get("text_zh") or CONTROL_RE.search(r.get("text_zh", "")):
            _err(errors, "E_RULE_TEXT", "规则 %s 缺少单行文本" % rid, "/rules/%d" % i)
        if stage == "release" and r.get("level") in ("MUST", "NEVER") and r.get("review") == "pending":
            _err(errors, "E_PENDING_RULE", "MUST/NEVER 规则 %s 尚未审核" % rid, "/rules/%d" % i)
    for c in rule_contradictions(rules):
        _err(errors, "E_RULE_CONFLICT", "规则互相矛盾：%s（%s / %s）" % (", ".join(c["rules"]), c["subject"], c["action"]), "/rules")

    asset_ids = []
    for i, a in enumerate(ir.get("assets", [])):
        asset_ids.append(a.get("id"))
        try:
            safe_relpath(a.get("file"), "assets[%d].file" % i)
        except DBError as e:
            _err(errors, e.code, e.message, "/assets/%d/file" % i)
        if a.get("include") and a.get("redistribution_allowed") is not True:
            _err(errors, "E_LICENSE", "资产 %s 未获再分发许可，不能打包" % a.get("id"), "/assets/%d" % i)
    if len(set(asset_ids)) != len(asset_ids):
        _err(errors, "E_DUPLICATE", "资产 ID 重复", "/assets")
    logo = (brand.get("identity") or {}).get("logo_asset")
    if logo and logo not in asset_ids:
        _err(errors, "E_REF", "brand.identity.logo_asset 指向不存在的资产：%s" % logo, "/brand/identity")
    for i, f in enumerate(ir.get("fonts", [])):
        if f.get("bundled") and f.get("redistribution_allowed") is not True:
            _err(errors, "E_LICENSE", "字体 %s 不允许再分发，不能打包" % f.get("family"), "/fonts/%d" % i)

    gates = ir.get("gates") or {}
    for g in GATES:
        st = (gates.get(g) or {}).get("status")
        if st not in GATE_STATUS:
            _err(errors, "E_GATE", "Gate %s 状态非法：%r" % (g, st), "/gates/%s" % g)
    if stage == "release":
        for g in ("G1", "G2", "G3", "G4", "G5", "G6"):
            if (gates.get(g) or {}).get("status") != "KEEP":
                _err(errors, "E_GATE_OPEN", "Gate %s 尚未确认（KEEP）" % g, "/gates/%s" % g)
        blocking = [p for p in pending if p.startswith(("/brand", "/design_system", "/rules"))]
        if blocking:
            _err(errors, "E_PENDING", "仍有 %d 项待审核的事实" % len(blocking), blocking[0])
    return {"errors": errors, "warnings": warnings, "pending": pending}
