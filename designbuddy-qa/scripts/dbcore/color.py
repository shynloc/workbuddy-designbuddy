"""Colour maths: parsing, WCAG 2.x contrast, palette derivation."""
import colorsys

from .util import HEX_RE, DBError


def norm_hex(value, field="color"):
    if not isinstance(value, str) or not HEX_RE.match(value.strip()):
        raise DBError("E_COLOR", "%s 不是 #RRGGBB 格式的颜色：%r" % (field, value))
    return value.strip().upper()


def rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def to_hex(r, g, b):
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(round(v)))) for v in (r, g, b))


def _lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_color):
    r, g, b = rgb(hex_color)
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(fg, bg):
    a, b = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def grade(ratio, kind="text"):
    """WCAG 2.x AA. kind: text (4.5), large (3.0), ui (3.0 non-text)."""
    if kind in ("large", "ui"):
        return "PASS" if ratio >= 3.0 else "FAIL"
    if ratio >= 4.5:
        return "PASS"
    return "WARNING" if ratio >= 3.0 else "FAIL"


def _hls(hex_color):
    r, g, b = (v / 255.0 for v in rgb(hex_color))
    return colorsys.rgb_to_hls(r, g, b)


def _from_hls(h, l, s):
    r, g, b = colorsys.hls_to_rgb(h, max(0.0, min(1.0, l)), max(0.0, min(1.0, s)))
    return to_hex(r * 255, g * 255, b * 255)


def tint(hex_color, lightness):
    h, _l, s = _hls(hex_color)
    return _from_hls(h, lightness, s)


def neutral_ink(hex_color):
    """Very dark, slightly hue-tinted ink for body text."""
    h, _l, s = _hls(hex_color)
    return _from_hls(h, 0.11, min(s, 0.25))


def neutral_surface(hex_color):
    h, _l, s = _hls(hex_color)
    return _from_hls(h, 0.965, min(s, 0.6))


def darken_until(fg, bg, target=4.5, step=0.02):
    """Return the closest darker/lighter variant of fg that reaches target on bg."""
    h, l, s = _hls(fg)
    darker = luminance(bg) > 0.18
    cur = fg
    for _ in range(60):
        if contrast(cur, bg) >= target:
            return cur
        l = l - step if darker else l + step
        cur = _from_hls(h, l, s)
    return cur


def best_on(bg, light="#FFFFFF", dark="#111111"):
    return light if contrast(light, bg) >= contrast(dark, bg) else dark
