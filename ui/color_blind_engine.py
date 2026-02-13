"""Color-blind safe palette utilities based on Wong 2011 (Nature Methods)."""

import math

# Wong 2011 color-blind safe palette
WONG_PALETTE = {
    "black": "#000000",
    "orange": "#E69F00",
    "sky_blue": "#56B4E9",
    "bluish_green": "#009E73",
    "yellow": "#F0E442",
    "blue": "#0072B2",
    "vermillion": "#D55E00",
    "reddish_purple": "#CC79A7",
}


def _hex_to_rgb(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _relative_luminance(r: int, g: int, b: int) -> float:
    """WCAG 2.x relative luminance."""
    def linearize(c):
        cs = c / 255.0
        return cs / 12.92 if cs <= 0.04045 else ((cs + 0.055) / 1.055) ** 2.4
    return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)


def validate_contrast(fg_hex: str, bg_hex: str) -> float:
    """Return WCAG contrast ratio between two hex colors."""
    l1 = _relative_luminance(*_hex_to_rgb(fg_hex))
    l2 = _relative_luminance(*_hex_to_rgb(bg_hex))
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def get_safe_palette() -> dict:
    """Return the Wong 2011 palette dict."""
    return dict(WONG_PALETTE)


def passes_aa(fg_hex: str, bg_hex: str, large_text: bool = False) -> bool:
    ratio = validate_contrast(fg_hex, bg_hex)
    return ratio >= 3.0 if large_text else ratio >= 4.5


def passes_aaa(fg_hex: str, bg_hex: str, large_text: bool = False) -> bool:
    ratio = validate_contrast(fg_hex, bg_hex)
    return ratio >= 4.5 if large_text else ratio >= 7.0
