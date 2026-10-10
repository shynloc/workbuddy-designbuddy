#!/usr/bin/env python3
"""WCAG 2.x contrast checker (standard library only).

Usage:
    python3 validate_contrast.py FG BG [--large]
    python3 validate_contrast.py --tokens <tokens.json>   # checks declared pairs

Result per pair: PASS / WARNING / FAIL
  normal text: PASS >= 4.5, WARNING >= 3.0 (large-text only), FAIL < 3.0
  large text / UI: PASS >= 3.0, FAIL < 3.0
"""
import json
import sys
from pathlib import Path


def _lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_color):
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    if len(h) != 6:
        raise ValueError("bad color: %s" % hex_color)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def ratio(fg, bg):
    a, b = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def grade(r, large=False):
    if large:
        return "PASS" if r >= 3.0 else "FAIL"
    if r >= 4.5:
        return "PASS"
    return "WARNING" if r >= 3.0 else "FAIL"


def main(argv):
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:  # noqa: BLE001
        pass
    if len(argv) >= 2 and argv[0] == "--tokens":
        data = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
        flat = {}

        def walk(node, prefix):
            for k, v in node.items():
                if k.startswith("$"):
                    continue
                if isinstance(v, dict) and "$value" in v:
                    flat[prefix + k] = v["$value"]
                elif isinstance(v, dict):
                    walk(v, prefix + k + ".")

        walk(data, "")
        pairs = data.get("$extensions", {}).get("dbprobe.contrastPairs", [])
        worst = "PASS"
        for p in pairs:
            fg, bg = flat[p["fg"]], flat[p["bg"]]
            r = ratio(fg, bg)
            g = grade(r, p.get("large", False))
            if g == "FAIL" or (g == "WARNING" and worst == "PASS"):
                worst = g
            print("[%s] %-28s %s on %s = %.2f:1 %s" % (g, p["name"], fg, bg, r, "(large)" if p.get("large") else ""))
        print("overall: %s" % worst)
        return 1 if worst == "FAIL" else 0
    if len(argv) >= 2:
        r = ratio(argv[0], argv[1])
        g = grade(r, "--large" in argv)
        print("[%s] %s on %s = %.2f:1" % (g, argv[0], argv[1], r))
        return 1 if g == "FAIL" else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
