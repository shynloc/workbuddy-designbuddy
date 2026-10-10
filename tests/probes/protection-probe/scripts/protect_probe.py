#!/usr/bin/env python3
"""DesignBuddy protection probe — what still works when a skill is paid/encrypted?

Answers, from inside the real WorkBuddy skill runtime:
  P-EXEC         can this bundled script run at all?
  P-SRC-READ     can the script read its own source file as plain text?
  P-RES-READ     can it read bundled templates (resources) it needs?
  P-RES-EXPORT   can it write a template's content into the user's workspace?
  P-GEN-EMBED    can it generate a new file purely from embedded data?
  P-GEN-RENDER   can it render a bundled template + tokens into a new file
                 (the real DesignBuddy compiler pattern)?
  P-INVENTORY    which bundled files are readable, and do they look like plain text?

Standard library only. Writes only under <cwd>/dbprobe-results/protection/.
"""
import argparse
import datetime as _dt
import hashlib
import json
import sys
import uuid
from pathlib import Path

PROBE_VERSION = "1.0.0"
SCRIPT_MARKER = "DBP-PRO-SCR-4H8T"
MARKERS = {
    "SKILL.md": "DBP-PRO-SKL-2W6R",
    "references/protected-reference.md": "DBP-PRO-REF-7Q3K",
    "templates/protected-template.txt": "DBP-PRO-TPL-9M2X",
    "templates/component.html": "DBP-PRO-CMP-3F5J",
    "scripts/protect_probe.py": SCRIPT_MARKER,
}
SKILL_DIR = Path(__file__).resolve().parent.parent
TOKENS = {"brand.primary": "#1F4FD8", "brand.on-primary": "#FFFFFF", "font.heading": "Source Han Sans SC"}


def run(out_dir):
    checks = []

    def add(cid, result, detail):
        checks.append({"id": cid, "result": result, "detail": detail})

    add("P-EXEC", "PASS", {"marker_from_code": SCRIPT_MARKER, "python": sys.version.split()[0]})

    # Own source as text
    try:
        src = Path(__file__).read_text(encoding="utf-8")
        add("P-SRC-READ", "PASS" if SCRIPT_MARKER in src else "PARTIAL",
            {"plaintext_marker_found": SCRIPT_MARKER in src, "bytes": len(src.encode("utf-8"))})
    except Exception as e:  # noqa: BLE001
        add("P-SRC-READ", "FAIL", {"error": "%s: %s" % (type(e).__name__, e)})

    # Bundled resources
    tpl_text = None
    try:
        tpl_text = (SKILL_DIR / "templates" / "protected-template.txt").read_text(encoding="utf-8")
        found = MARKERS["templates/protected-template.txt"] in tpl_text
        add("P-RES-READ", "PASS" if found else "PARTIAL", {"marker_found": found})
    except Exception as e:  # noqa: BLE001
        add("P-RES-READ", "FAIL", {"error": "%s: %s" % (type(e).__name__, e)})

    # Export a bundled template into the user's workspace
    try:
        if tpl_text is None:
            raise RuntimeError("template was not readable")
        out_dir.mkdir(parents=True, exist_ok=True)
        dst = out_dir / "exported-template.txt"
        dst.write_text(tpl_text, encoding="utf-8")
        ok = MARKERS["templates/protected-template.txt"] in dst.read_text(encoding="utf-8")
        add("P-RES-EXPORT", "PASS" if ok else "FAIL", {"file": str(dst)})
    except Exception as e:  # noqa: BLE001
        add("P-RES-EXPORT", "FAIL", {"error": "%s: %s" % (type(e).__name__, e)})

    # Generate from embedded data only (no bundled file read)
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        css = ":root{\n" + "".join("  --%s: %s;\n" % (k.replace(".", "-"), v) for k, v in TOKENS.items()) + "}\n"
        dst = out_dir / "generated-tokens.css"
        dst.write_text(css, encoding="utf-8")
        add("P-GEN-EMBED", "PASS", {"file": str(dst)})
    except Exception as e:  # noqa: BLE001
        add("P-GEN-EMBED", "FAIL", {"error": "%s: %s" % (type(e).__name__, e)})

    # Render bundled component template + tokens into a new file
    try:
        comp = (SKILL_DIR / "templates" / "component.html").read_text(encoding="utf-8")
        html = comp
        for k, v in TOKENS.items():
            html = html.replace("{{%s}}" % k, v)
        dst = out_dir / "rendered-component.html"
        dst.write_text(html, encoding="utf-8")
        ok = "{{" not in html and TOKENS["brand.primary"] in html
        add("P-GEN-RENDER", "PASS" if ok else "PARTIAL", {"file": str(dst), "all_tokens_resolved": ok})
    except Exception as e:  # noqa: BLE001
        add("P-GEN-RENDER", "FAIL", {"error": "%s: %s" % (type(e).__name__, e)})

    # Inventory of the installed package as seen from disk
    inv = {}
    try:
        for p in sorted(SKILL_DIR.rglob("*")):
            if not p.is_file() or "__pycache__" in p.parts:
                continue
            rel = p.relative_to(SKILL_DIR).as_posix()
            try:
                data = p.read_bytes()
                marker = MARKERS.get(rel)
                inv[rel] = {
                    "bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest()[:16],
                    "plaintext_marker": (marker.encode() in data) if marker else None,
                }
            except Exception as e:  # noqa: BLE001
                inv[rel] = {"error": "%s: %s" % (type(e).__name__, e)}
        missing = [r for r in MARKERS if r not in inv]
        add("P-INVENTORY", "PASS", {"skill_dir": str(SKILL_DIR), "files": inv, "expected_but_not_found": missing})
    except Exception as e:  # noqa: BLE001
        add("P-INVENTORY", "FAIL", {"error": "%s: %s" % (type(e).__name__, e)})
    return checks


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:  # noqa: BLE001
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    out_dir = Path(args.out) if args.out else Path.cwd() / "dbprobe-results" / "protection"
    checks = run(out_dir)
    run_id = "protect-%s-%s" % (_dt.datetime.now().strftime("%Y%m%d-%H%M%S"), uuid.uuid4().hex[:4])
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        rf = out_dir / (run_id + ".json")
        rf.write_text(json.dumps({"probe": "dbprobe-protection", "probe_version": PROBE_VERSION,
                                  "run_id": run_id, "checks": checks}, ensure_ascii=False, indent=2),
                      encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        rf = "NOT SAVED: %s" % e
    print("=== DBPROBE REPORT BEGIN ===")
    print("probe: dbprobe-protection %s" % PROBE_VERSION)
    print("run_id: %s" % run_id)
    print("result_file: %s" % rf)
    for c in checks:
        print("- [%s] %s" % (c["result"], c["id"]))
        print("    %s" % json.dumps(c["detail"], ensure_ascii=False))
    print("=== DBPROBE REPORT END ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
