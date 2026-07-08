"""
Logo Generator — шаблонный движок: Phosphor Icons (MIT) + OFL шрифты.

Принципы:
- SVG полностью самодостаточен: нет <text>, нет @import — только <path>
- Текст конвертируется в контуры букв через fontTools (OFL шрифты)
- Иконки: Phosphor Icons fill-variant, viewBox 0 0 256 256
- Детерминированный: одни и те же входные данные → одинаковый SVG
- Синхронный, без внешних API-вызовов

Шрифты: backend/app/assets/fonts/  (python scripts/download_fonts.py)
Иконки: backend/app/assets/icons/  (python scripts/copy_icons.py)
Лицензии: SIL OFL 1.1 (шрифты), MIT (Phosphor Icons).
"""
from __future__ import annotations

import colorsys
import hashlib
import random
import re
import xml.etree.ElementTree as _ET
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

# ---------------------------------------------------------------------------
# Icon infrastructure — Phosphor Icons fill, viewBox 0 0 256 256 (MIT)
# ---------------------------------------------------------------------------

_ICONS_DIR = Path(__file__).parent.parent / "assets" / "icons"
_icon_svg_cache: Dict[str, str] = {}
_SVG_NS = "{http://www.w3.org/2000/svg}"


def _load_icon_svg(name: str) -> str:
    """Return serialised inner SVG markup for a Phosphor fill icon.

    The returned string contains only the child elements (path, etc.) with
    namespace stripped and fill removed — fill is set on the wrapping <g>.
    Fallback to a filled circle if the file is missing.
    """
    if name in _icon_svg_cache:
        return _icon_svg_cache[name]

    icon_path = _ICONS_DIR / f"{name}.svg"
    if not icon_path.exists():
        _icon_svg_cache[name] = '<circle cx="128" cy="128" r="96"/>'
        return _icon_svg_cache[name]

    root = _ET.parse(str(icon_path)).getroot()
    parts: List[str] = []
    for child in root:
        tag = child.tag.replace(_SVG_NS, "")
        attrs = {
            k.replace(_SVG_NS, ""): v
            for k, v in child.attrib.items()
            if k.replace(_SVG_NS, "") != "fill"
        }
        attr_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())
        parts.append(f"<{tag} {attr_str}/>")

    result = "".join(parts)
    _icon_svg_cache[name] = result
    return result


# ---------------------------------------------------------------------------
# Font infrastructure
# ---------------------------------------------------------------------------

_FONTS_DIR = Path(__file__).parent.parent / "assets" / "fonts"
_font_cache: Dict[str, TTFont] = {}


def _load_font(filename: str) -> TTFont:
    if filename not in _font_cache:
        path = _FONTS_DIR / filename
        if not path.exists():
            raise FileNotFoundError(
                f"Font not found: {path}\n"
                "Run: cd backend && python scripts/download_fonts.py"
            )
        _font_cache[filename] = TTFont(str(path))
    return _font_cache[filename]


def preload_fonts() -> None:
    """Load all font files into cache. Call once at app startup to avoid
    first-request latency."""
    for pair in _FONT_PAIRS:
        _load_font(pair.heading_file)
        _load_font(pair.body_file)


def _text_width(
    text: str,
    font: TTFont,
    size: float,
    spacing: float = 0.0,
) -> float:
    """Total advance width of ``text`` in SVG px, including inter-glyph spacing."""
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    upm = font["head"].unitsPerEm
    scale = size / upm
    total = 0.0
    n_visible = 0
    for ch in text:
        cp = ord(ch)
        if cp == 0x20:
            total += size * 0.25
        elif cp in cmap and cmap[cp] in glyph_set:
            total += glyph_set[cmap[cp]].width * scale
        else:
            total += size * 0.35
        n_visible += 1
    if n_visible > 1:
        total += spacing * (n_visible - 1)
    return total


def _text_to_paths(
    text: str,
    font: TTFont,
    size: float,
    x: float,
    y_baseline: float,
    fill: str,
    spacing: float = 0.0,
) -> str:
    """
    Convert ``text`` to a series of SVG <path> elements.

    Font coordinate system has Y going up; SVG has Y going down.
    The per-glyph transform ``translate(x, y_baseline) scale(s, -s)``
    handles the flip: ascenders land above y_baseline, descenders below.
    """
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    upm = font["head"].unitsPerEm
    scale = size / upm
    parts: List[str] = []
    cur_x = x

    for ch in text:
        cp = ord(ch)
        if cp == 0x20:
            cur_x += size * 0.25 + spacing
            continue
        glyph_name = cmap.get(cp)
        if not glyph_name or glyph_name not in glyph_set:
            cur_x += size * 0.35 + spacing
            continue
        glyph = glyph_set[glyph_name]
        pen = SVGPathPen(glyph_set)
        glyph.draw(pen)
        d = pen.getCommands()
        if d:
            parts.append(
                f'<path transform="translate({cur_x:.2f},{y_baseline:.2f})'
                f' scale({scale:.5f},{-scale:.5f})"'
                f' d="{d}" fill="{fill}"/>'
            )
        cur_x += glyph.width * scale + spacing

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class LogoVariant:
    svg: bytes
    icon_name: str
    font_heading: str
    font_body: str
    palette: List[str]  # [primary, secondary, accent, text]
    layout: str         # "centered" | "horizontal" | "badge"


@dataclass
class _FontPair:
    heading: str       # display name for metadata
    body: str
    style_tag: str
    heading_file: str  # filename inside assets/fonts/
    body_file: str


# ---------------------------------------------------------------------------
# Industry → icon pool  (Phosphor Icons fill, files in app/assets/icons/)
# ---------------------------------------------------------------------------

_INDUSTRY_ICONS: Dict[str, List[str]] = {
    "tech":       ["cpu", "code", "cloud", "rocket", "circuitry"],
    "healthcare": ["heart", "stethoscope", "first-aid-kit", "pill", "dna"],
    "finance":    ["currency-dollar", "chart-line-up", "bank", "coins", "hand-coins"],
    "food":       ["coffee", "pizza", "fork-knife", "bowl-food", "cooking-pot"],
    "creative":   ["palette", "paint-brush", "pen-nib", "camera", "music-note"],
    "retail":     ["shopping-bag", "tag", "storefront", "coat-hanger", "gift"],
    "fitness":    ["barbell", "bicycle", "person-simple-run", "trophy", "medal"],
    "education":  ["book-open", "graduation-cap", "pencil", "chalkboard", "atom"],
    "consulting": ["briefcase", "handshake", "chart-bar", "lightbulb", "users"],
    "other":      ["star", "diamond", "crown", "sparkle", "globe"],
}

# ---------------------------------------------------------------------------
# Google Fonts pairs — OFL licensed, files in assets/fonts/
# ---------------------------------------------------------------------------

_FONT_PAIRS: List[_FontPair] = [
    _FontPair(
        heading="Montserrat", body="Open Sans",
        style_tag="modern",
        heading_file="Montserrat-SemiBold.woff2",
        body_file="OpenSans-Regular.woff2",
    ),
    _FontPair(
        heading="Playfair Display", body="Lato",
        style_tag="classic",
        heading_file="PlayfairDisplay-Bold.woff2",
        body_file="Lato-Regular.ttf",
    ),
    _FontPair(
        heading="DM Sans", body="DM Mono",
        style_tag="minimal",
        heading_file="DMSans-SemiBold.woff2",
        body_file="DMMono-Regular.woff2",
    ),
    _FontPair(
        heading="Nunito", body="Nunito",
        style_tag="playful",
        heading_file="Nunito-Bold.woff2",
        body_file="Nunito-Bold.woff2",
    ),
    _FontPair(
        heading="Oswald", body="Source Sans 3",
        style_tag="bold",
        heading_file="Oswald-SemiBold.woff2",
        body_file="SourceSans3-Regular.woff2",
    ),
    _FontPair(
        heading="Cormorant Garamond", body="Jost",
        style_tag="elegant",
        heading_file="CormorantGaramond-SemiBold.woff2",
        body_file="Jost-Light.woff2",
    ),
    _FontPair(
        heading="Space Grotesk", body="Inter",
        style_tag="tech",
        heading_file="SpaceGrotesk-SemiBold.woff2",
        body_file="Inter-Regular.woff2",
    ),
    _FontPair(
        heading="Raleway", body="Mulish",
        style_tag="geometric",
        heading_file="Raleway-Bold.woff2",
        body_file="Mulish-Light.woff2",
    ),
]

_PREF_STYLE_MAP: Dict[str, str] = {
    "modern": "modern", "contemporary": "modern",
    "classic": "classic", "traditional": "classic",
    "minimal": "minimal", "minimalist": "minimal",
    "playful": "playful", "fun": "playful",
    "bold": "bold", "strong": "bold",
    "elegant": "elegant", "sophisticated": "elegant",
    "tech": "tech", "technology": "tech",
    "geometric": "geometric",
}

# ---------------------------------------------------------------------------
# Color utilities
# ---------------------------------------------------------------------------


def _hex_to_hsl(hex_color: str) -> Tuple[float, float, float]:
    h_str = hex_color.lstrip("#")
    r, g, b = (int(h_str[i: i + 2], 16) / 255.0 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h, s, l


def _hsl_to_hex(h: float, s: float, l: float) -> str:
    h = h % 1.0
    s = max(0.0, min(1.0, s))
    l = max(0.0, min(1.0, l))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return "#{:02x}{:02x}{:02x}".format(round(r * 255), round(g * 255), round(b * 255))


_INDUSTRY_BASE_COLORS: Dict[str, str] = {
    "tech":       "#2563eb",
    "healthcare": "#059669",
    "finance":    "#1e3a5f",
    "food":       "#ea580c",
    "creative":   "#7c3aed",
    "retail":     "#db2777",
    "fitness":    "#f97316",
    "education":  "#0369a1",
    "consulting": "#374151",
    "other":      "#0f766e",
}

_PALETTE_SCHEMES = ("complement", "analogous", "monochrome")

_HEX_RE = re.compile(r'^#[0-9a-fA-F]{6}$')


def _parse_color(colors: list) -> Optional[str]:
    """Return the first valid 6-digit hex color from the list, or None."""
    for c in colors:
        if isinstance(c, str) and _HEX_RE.match(c):
            return c.lower()
    return None


def _generate_palette(base_hex: str, scheme: str) -> List[str]:
    """Return [primary, secondary, accent, text] hex strings."""
    h, s, l = _hex_to_hsl(base_hex)
    if scheme == "complement":
        primary   = base_hex
        secondary = _hsl_to_hex(h + 0.5, s, l)
        accent    = _hsl_to_hex(h, max(0.15, s - 0.2), min(0.88, l + 0.22))
        text      = _hsl_to_hex(h, max(0.08, s * 0.3), 0.14)
    elif scheme == "analogous":
        primary   = base_hex
        secondary = _hsl_to_hex(h + 1 / 12, s, l)
        accent    = _hsl_to_hex(h - 1 / 12, s, l)
        text      = _hsl_to_hex(h, max(0.08, s * 0.35), 0.14)
    else:  # monochrome
        primary   = base_hex
        secondary = _hsl_to_hex(h, max(0.0, s - 0.12), min(0.92, l + 0.28))
        accent    = _hsl_to_hex(h, s, max(0.08, l - 0.22))
        text      = _hsl_to_hex(h, max(0.08, s * 0.25), 0.12)
    return [primary, secondary, accent, text]


# ---------------------------------------------------------------------------
# Industry detection
# ---------------------------------------------------------------------------

_INDUSTRY_KEYWORDS: Dict[str, List[str]] = {
    "tech":       ["tech", "software", "ai", "digital", "data", "cloud", "cyber", "dev", "saas", "platform", "app", "ml", "analytics"],
    "healthcare": ["health", "medical", "care", "clinic", "hospital", "wellness", "therapy", "pharma", "dental"],
    "finance":    ["finance", "bank", "invest", "trading", "capital", "wealth", "insurance", "fund", "fintech"],
    "food":       ["food", "restaurant", "cafe", "coffee", "chef", "culinary", "bakery", "catering", "kitchen", "dining"],
    "creative":   ["design", "creative", "art", "studio", "agency", "media", "photo", "video", "animation"],
    "retail":     ["retail", "shop", "store", "fashion", "clothing", "boutique", "ecommerce"],
    "fitness":    ["sport", "sports", "athletic", "fitness", "gym", "yoga", "running", "outdoor", "activewear", "sportswear", "apparel", "sneaker", "shoe"],
    "education":  ["education", "school", "university", "learning", "academy", "training", "course", "edtech"],
    "consulting": ["consulting", "advisory", "strategy", "management", "solutions", "services", "professional"],
}


def _detect_industry(business_type: str) -> str:
    text = business_type.lower()
    scores = {
        ind: sum(1 for kw in kws if kw in text)
        for ind, kws in _INDUSTRY_KEYWORDS.items()
    }
    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else "other"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_seed(business_name: str) -> int:
    digest = hashlib.md5(business_name.lower().strip().encode()).hexdigest()
    return int(digest, 16) % (2 ** 32)


def _xml_escape(text: str) -> str:
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _short_tagline(business_type: str) -> str:
    words = business_type.split()
    return " ".join(words[:3])[:30]


def _icon_group(icon_name: str, color: str, size: float) -> str:
    """SVG <g> rendering a Phosphor fill icon at (0,0) scaled to `size`×`size`.

    Phosphor icons have viewBox 0 0 256 256, so scale = size / 256.
    fill is set directly on the group; stroke is disabled.
    """
    inner = _load_icon_svg(icon_name)
    scale = size / 256.0
    return (
        f'<g transform="scale({scale:.5f})" fill="{color}" stroke="none">'
        f"{inner}"
        f"</g>"
    )


# ---------------------------------------------------------------------------
# SVG layouts — text rendered as <path> outlines, no <text> or @import
# ---------------------------------------------------------------------------

def _render_centered(
    name: str,
    icon_name: str,
    font: _FontPair,
    palette: List[str],
) -> str:
    W, H = 480, 300
    primary, _secondary, _accent, text_color = palette
    icon_size = 68.0
    cx = W / 2
    name_size = 30.0

    circle_r = icon_size * 0.62
    cap_h = name_size * 0.72
    gap = 20.0
    total_h = circle_r * 2 + gap + cap_h
    cy = (H - total_h) / 2 + circle_r
    name_y = cy + circle_r + gap + cap_h

    icon_x = cx - icon_size / 2
    icon_y = cy - icon_size / 2

    h_font = _load_font(font.heading_file)

    name_w = _text_width(name, h_font, name_size)
    name_paths = _text_to_paths(
        name, h_font, name_size, cx - name_w / 2, name_y, text_color
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}">\n'
        f'  <rect width="{W}" height="{H}" fill="#ffffff"/>\n'
        f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{icon_size * 0.62:.1f}" fill="{primary}"/>\n'
        f'  <g transform="translate({icon_x:.1f},{icon_y:.1f})">'
        + _icon_group(icon_name, "#ffffff", icon_size) +
        f'</g>\n'
        + name_paths + "\n"
        + "</svg>"
    )


def _render_horizontal(
    name: str,
    icon_name: str,
    font: _FontPair,
    palette: List[str],
) -> str:
    W, H = 520, 160
    primary, _secondary, accent, text_color = palette
    icon_size = 60.0
    pad = 30.0
    cx = pad + icon_size / 2
    cy = H / 2
    icon_x = cx - icon_size / 2
    icon_y = cy - icon_size / 2
    text_x = pad * 2 + icon_size + 8

    h_font = _load_font(font.heading_file)

    name_size = 34.0
    # Baseline that centers 34px cap height vertically in the canvas
    name_y = cy + name_size * 0.36

    name_paths = _text_to_paths(name, h_font, name_size, text_x, name_y, text_color)

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}">\n'
        f'  <rect width="{W}" height="{H}" fill="#ffffff"/>\n'
        f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{icon_size * 0.62:.1f}" fill="{primary}"/>\n'
        f'  <g transform="translate({icon_x:.1f},{icon_y:.1f})">'
        + _icon_group(icon_name, "#ffffff", icon_size) +
        f'</g>\n'
        f'  <line x1="{text_x - 10:.1f}" y1="{H * 0.18:.1f}" '
        f'x2="{text_x - 10:.1f}" y2="{H * 0.82:.1f}" '
        f'stroke="{accent}" stroke-width="1.5" opacity="0.5"/>\n'
        + name_paths + "\n"
        + "</svg>"
    )


def _render_badge(
    name: str,
    icon_name: str,
    font: _FontPair,
    palette: List[str],
) -> str:
    W, H = 300, 300
    primary, _secondary, _accent, text_color = palette
    pad = 22
    icon_size = 54.0
    cx = W / 2
    name_size = 24.0

    circle_r = icon_size * 0.62
    cap_h = name_size * 0.72
    gap = 16.0
    inner_h = float(H - 2 * pad)
    total_h = circle_r * 2 + gap + cap_h
    cy = pad + (inner_h - total_h) / 2 + circle_r
    name_y = cy + circle_r + gap + cap_h

    icon_x = cx - icon_size / 2
    icon_y = cy - icon_size / 2

    h_font = _load_font(font.heading_file)

    name_w = _text_width(name, h_font, name_size)
    name_paths = _text_to_paths(
        name, h_font, name_size, cx - name_w / 2, name_y, text_color
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}">\n'
        f'  <rect width="{W}" height="{H}" fill="#ffffff"/>\n'
        f'  <rect x="{pad}" y="{pad}" width="{W - pad * 2}" height="{H - pad * 2}" '
        f'rx="22" fill="{primary}" opacity="0.07"/>\n'
        f'  <rect x="{pad}" y="{pad}" width="{W - pad * 2}" height="{H - pad * 2}" '
        f'rx="22" fill="none" stroke="{primary}" stroke-width="1.5" opacity="0.25"/>\n'
        f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{icon_size * 0.62:.1f}" fill="{primary}"/>\n'
        f'  <g transform="translate({icon_x:.1f},{icon_y:.1f})">'
        + _icon_group(icon_name, "#ffffff", icon_size) +
        f'</g>\n'
        + name_paths + "\n"
        + "</svg>"
    )


_LAYOUTS = ("centered", "horizontal", "badge")

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_logo_variants(
    business_name: str,
    business_type: str,
    prefs: Optional[dict] = None,
    count: int = 4,
) -> List[LogoVariant]:
    """
    Generate ``count`` deterministic logo variants.

    Args:
        business_name: Display name used in the logo text ("Acme Corp").
        business_type: Free-text description ("AI tech startup…").
        prefs: Optional dict:
            - style: str  — "modern"|"classic"|"playful"|"minimal"|"bold"|
                           "elegant"|"tech"|"geometric"
            - colors: list[str]  — first hex (#RRGGBB) used as palette base
        count: Number of variants to return (default 4).

    Returns:
        List[LogoVariant] — each with .svg (bytes), .icon_name, .font_heading,
        .font_body, .palette, .layout.

    All text is rendered as SVG <path> outlines; the SVG contains no <text>
    elements and no external font references — suitable for Illustrator, Figma,
    print workflows, and offline viewing.
    """
    if prefs is None:
        prefs = {}

    name = ((prefs.get("business_name") or business_name).strip() or "Brand")[:60]
    seed = _make_seed(name)
    rng  = random.Random(seed)

    pref_industry = prefs.get("industry", "")
    if pref_industry and pref_industry in _INDUSTRY_ICONS:
        industry = pref_industry
    else:
        industry = _detect_industry(business_type)
    icon_pool = _INDUSTRY_ICONS.get(industry, _INDUSTRY_ICONS["other"])

    user_color = _parse_color(prefs.get("colors", []))
    base_color = user_color or _INDUSTRY_BASE_COLORS[industry]

    pref_style      = prefs.get("style", "")
    mapped_style    = _PREF_STYLE_MAP.get(pref_style.lower(), "")
    preferred_fonts = [fp for fp in _FONT_PAIRS if fp.style_tag == mapped_style]
    all_fonts       = (preferred_fonts + _FONT_PAIRS) if preferred_fonts else _FONT_PAIRS

    variants: List[LogoVariant] = []
    used_icons: set     = set()
    used_headings: set  = set()

    for i in range(count):
        available_icons = [ic for ic in icon_pool if ic not in used_icons]
        if not available_icons:
            available_icons = list(icon_pool)
        icon_name = available_icons[rng.randrange(len(available_icons))]
        used_icons.add(icon_name)

        # Variant 0 honours the style pref explicitly; rest cycle through all fonts
        if i == 0 and preferred_fonts:
            font_pool = preferred_fonts
        else:
            font_pool = [fp for fp in all_fonts if fp.heading not in used_headings]
            if not font_pool:
                font_pool = all_fonts
        font = font_pool[rng.randrange(len(font_pool))]
        used_headings.add(font.heading)

        scheme  = _PALETTE_SCHEMES[i % len(_PALETTE_SCHEMES)]
        palette = _generate_palette(base_color, scheme)

        layout = _LAYOUTS[i % len(_LAYOUTS)]

        if layout == "centered":
            svg_str = _render_centered(name, icon_name, font, palette)
        elif layout == "horizontal":
            svg_str = _render_horizontal(name, icon_name, font, palette)
        else:
            svg_str = _render_badge(name, icon_name, font, palette)

        variants.append(LogoVariant(
            svg=svg_str.encode("utf-8"),
            icon_name=icon_name,
            font_heading=font.heading,
            font_body=font.body,
            palette=palette,
            layout=layout,
        ))

    return variants
