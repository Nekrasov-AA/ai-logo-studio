"""
Logo Generator — шаблонный движок: Tabler Icons (MIT) + OFL шрифты.

Заменяет: worker/src/premium_engine.py, hybrid_ai.py, ai_visual_generator.py,
          logo_ai.py, geometric_ai.py (старые файлы НЕ удалены).

Принципы:
- SVG полностью самодостаточен: нет <text>, нет @import — только <path>
- Текст конвертируется в контуры букв через fontTools (OFL шрифты)
- Детерминированный: одни и те же входные данные → одинаковый SVG
- Синхронный, без внешних API-вызовов

Шрифты лежат в backend/app/assets/fonts/ (скачать: python scripts/download_fonts.py)
Лицензии шрифтов: SIL Open Font License 1.1 — допускает встраивание в продукты.
Иконки: Tabler Icons (MIT) — https://github.com/tabler/tabler-icons
"""
from __future__ import annotations

import colorsys
import hashlib
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont

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
# Tabler Icons — curated SVG inner markup (MIT License)
# Source: https://github.com/tabler/tabler-icons
# viewBox 0 0 24 24, stroke-based (fill=none), unless explicitly noted.
# Elements inherit stroke="currentColor" stroke-width="2" from parent <g>.
# ---------------------------------------------------------------------------

_ICONS: Dict[str, str] = {

    # ---- tech ----
    "device-laptop": (
        '<rect x="3" y="4" width="18" height="12" rx="1"/>'
        '<path d="M1 20h22"/>'
    ),
    "cpu": (
        '<rect x="7" y="7" width="10" height="10" rx="1"/>'
        '<line x1="9" y1="7" x2="9" y2="3"/>'
        '<line x1="12" y1="7" x2="12" y2="3"/>'
        '<line x1="15" y1="7" x2="15" y2="3"/>'
        '<line x1="9" y1="21" x2="9" y2="17"/>'
        '<line x1="12" y1="21" x2="12" y2="17"/>'
        '<line x1="15" y1="21" x2="15" y2="17"/>'
        '<line x1="7" y1="9" x2="3" y2="9"/>'
        '<line x1="7" y1="12" x2="3" y2="12"/>'
        '<line x1="7" y1="15" x2="3" y2="15"/>'
        '<line x1="21" y1="9" x2="17" y2="9"/>'
        '<line x1="21" y1="12" x2="17" y2="12"/>'
        '<line x1="21" y1="15" x2="17" y2="15"/>'
    ),
    "cloud": (
        '<path d="M6.657 18C4.085 18 2 15.993 2 13.517c0-2.475 2.085-4.482 '
        '4.657-4.482.32 0 .634.031.938.09C8.59 7.908 10.19 7 12 7c2.808 0 5 '
        '2.036 5 4.5V13a3 3 0 0 1-3 3H6.657z"/>'
    ),
    "wifi": (
        '<path d="M12 18h.01"/>'
        '<path d="M9.172 15.172a4 4 0 0 1 5.656 0"/>'
        '<path d="M6.343 12.343a8 8 0 0 1 11.314 0"/>'
        '<path d="M3.515 9.515c4.686-4.686 12.284-4.686 16.97 0"/>'
    ),
    "code": (
        '<polyline points="16 18 22 12 16 6"/>'
        '<polyline points="8 6 2 12 8 18"/>'
    ),
    "layers": (
        '<polygon points="12 2 2 7 12 12 22 7 12 2"/>'
        '<polyline points="2 17 12 22 22 17"/>'
        '<polyline points="2 12 12 17 22 12"/>'
    ),
    "bolt": (
        '<path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"'
        ' fill="currentColor" stroke="none"/>'
    ),

    # ---- healthcare ----
    "heart-pulse": (
        '<path d="M19.5 12.572L12 20l-7.5-7.428A5 5 0 1 1 12 5.006a5 5 0 1 1 7.5 7.566"/>'
        '<polyline points="0 13 4 13 7 7 10 17 13 11 16 15 18 13 24 13"/>'
    ),
    "shield-check": (
        '<path d="M12 3l7 3.5V11c0 4.27-2.913 8.228-7 9.5C7.913 19.228 5 15.27 5 11V6.5L12 3z"/>'
        '<polyline points="9 12 11 14 15 10"/>'
    ),
    "leaf": (
        '<path d="M5 21c0 0 0-8 7-13 7-5 13-4 13-4s1 6-4 11S5 21 5 21"/>'
        '<path d="M5 21l7-8"/>'
    ),
    "activity": (
        '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>'
    ),
    "stethoscope": (
        '<path d="M6 3a3 3 0 0 0-3 3v3a6 6 0 0 0 12 0V6a3 3 0 0 0-3-3"/>'
        '<path d="M18 14a4 4 0 1 0 0 4h0a4 4 0 0 0 0-4"/>'
        '<path d="M15 12v2a3 3 0 0 0 3 3"/>'
    ),

    # ---- finance ----
    "trending-up": (
        '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>'
        '<polyline points="16 7 22 7 22 13"/>'
    ),
    "coin": (
        '<circle cx="12" cy="12" r="9"/>'
        '<path d="M14.8 9a2 2 0 0 0-2-1h-1.6a2 2 0 0 0 0 4h1.6a2 2 0 0 1 0 4H11a2 2 0 0 1-2-1"/>'
        '<line x1="12" y1="7" x2="12" y2="9"/>'
        '<line x1="12" y1="15" x2="12" y2="17"/>'
    ),
    "building-bank": (
        '<line x1="3" y1="21" x2="21" y2="21"/>'
        '<line x1="3" y1="10" x2="21" y2="10"/>'
        '<polyline points="5 10 5 21"/>'
        '<polyline points="19 10 19 21"/>'
        '<polyline points="9 10 9 21"/>'
        '<polyline points="15 10 15 21"/>'
        '<polyline points="12 10 12 21"/>'
        '<polyline points="2 10 12 3 22 10"/>'
    ),
    "chart-line": (
        '<rect x="3" y="4" width="18" height="16" rx="1"/>'
        '<polyline points="7 16 10 11 13 14 16 9 19 12"/>'
    ),
    "wallet": (
        '<path d="M17 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0 0 4h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-2"/>'
        '<path d="M20 12a2 2 0 0 0-2-2h-2a2 2 0 0 0 0 4h2a2 2 0 0 0 2-2z"/>'
    ),

    # ---- food ----
    "chef-hat": (
        '<path d="M9 11.5A4 4 0 1 1 12 8a4 4 0 1 1 3 3.5"/>'
        '<path d="M9 11.5V19a1 1 0 0 0 1 1h4a1 1 0 0 0 1-1v-7.5"/>'
        '<line x1="8" y1="15" x2="16" y2="15"/>'
    ),
    "coffee": (
        '<path d="M3 14c.83 2.87 3.33 5 5 5h6c1.67 0 4.17-2.13 5-5"/>'
        '<path d="M8 5v3M12 3v5M16 5v3"/>'
        '<rect x="2" y="13" width="20" height="2" rx="1"/>'
        '<path d="M20 15v2a2 2 0 0 0 2 2"/>'
    ),
    "salad": (
        '<path d="M7 21h10"/>'
        '<path d="M12 21a9 9 0 0 0 9-9H3a9 9 0 0 0 9 9z"/>'
        '<path d="M10 12a3 3 0 0 1 4-4"/>'
        '<path d="M14.5 7.5a3 3 0 0 1 2.5 4.5"/>'
        '<path d="M8 10.5A3.5 3.5 0 0 1 12 7"/>'
    ),
    "pizza": (
        '<path d="M12 21a9 9 0 0 0 9-9"/>'
        '<path d="M3 12a9 9 0 0 1 9-9"/>'
        '<path d="M12 3v9h9"/>'
        '<circle cx="11" cy="16" r="1" fill="currentColor" stroke="none"/>'
        '<circle cx="17" cy="11" r="1" fill="currentColor" stroke="none"/>'
    ),
    "apple": (
        '<path d="M12 20a8 8 0 1 0 0-16 8 8 0 0 0 0 16z"/>'
        '<path d="M12 4c0-1.1.5-2 1.2-2.4"/>'
        '<path d="M8 12c0-2.2 1.8-4 4-4s4 1.8 4 4"/>'
    ),

    # ---- creative ----
    "palette": (
        '<path d="M12 21a9 9 0 1 1 0-18 9 9 0 0 1 9 9c0 2.5-2 3-3 3a1.5 1.5 0 0 1-1.5-1.5'
        ' 1.5 1.5 0 0 0-1.5-1.5H12a3 3 0 0 1-3-3 6 6 0 0 1 1.8-4.3"/>'
        '<circle cx="8.5" cy="10.5" r="1" fill="currentColor" stroke="none"/>'
        '<circle cx="12.5" cy="8" r="1" fill="currentColor" stroke="none"/>'
        '<circle cx="16" cy="11" r="1" fill="currentColor" stroke="none"/>'
    ),
    "pencil": (
        '<path d="M4 20h4L18.5 9.5a2.83 2.83 0 0 0-4-4L4 16v4"/>'
        '<line x1="13.5" y1="6.5" x2="17.5" y2="10.5"/>'
    ),
    "brush": (
        '<path d="M3 21a6 6 0 0 0 6-6l7-7 3-3-3-3-3 3-7 7a6 6 0 0 0-3 6z"/>'
        '<circle cx="6" cy="18" r="2"/>'
    ),
    "stars": (
        '<path d="M17.8 19.2L16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2'
        'c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2'
        ' 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/>'
    ),
    "wand": (
        '<path d="M6 21L21 6l-3-3L3 18l3 3"/>'
        '<path d="M15 6l3 3"/>'
        '<path d="M9 3h1M18 13v1M12 2v1M3 12h1M20 4l1 1"/>'
    ),

    # ---- retail ----
    "shopping-bag": (
        '<path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/>'
        '<line x1="3" y1="6" x2="21" y2="6"/>'
        '<path d="M16 10a4 4 0 0 1-8 0"/>'
    ),
    "tag": (
        '<path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/>'
        '<line x1="7" y1="7" x2="7.01" y2="7"/>'
    ),
    "hanger": (
        '<path d="M20.05 16.45L12 12 3.95 16.45a2 2 0 1 0 2 3.46L12 16l6.05 3.91a2 2 0 1 0 2-3.46"/>'
        '<path d="M12 12V5.5"/>'
        '<circle cx="12" cy="4" r="1.5"/>'
    ),
    "shirt": (
        '<path d="M15 4l3 3-8.5 8.5a2.5 2.5 0 0 1-2.5-2.5l.5-1.5L4 9l3-5"/>'
        '<path d="M9 4L6 7l8.5 8.5a2.5 2.5 0 0 0 2.5-2.5L16.5 11.5 20 9l-3-5"/>'
    ),
    "package": (
        '<polyline points="21 8 21 21 3 21 3 8"/>'
        '<rect x="1" y="3" width="22" height="5"/>'
        '<line x1="10" y1="12" x2="14" y2="12"/>'
    ),

    # ---- education ----
    "book-open": (
        '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>'
        '<path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>'
    ),
    "school": (
        '<path d="M22 9L12 5 2 9l10 4 10-4v6"/>'
        '<path d="M6 11v5c0 2 2 4 6 4s6-2 6-4v-5"/>'
    ),
    "microscope": (
        '<path d="M7 3a1 1 0 0 0-1 1v5a1 1 0 0 0 1 1h2a1 1 0 0 0 1-1V4a1 1 0 0 0-1-1H7z"/>'
        '<path d="M12 10l5 5"/>'
        '<path d="M3 21h18"/>'
        '<path d="M12 10a4 4 0 1 0 5.66 5.66"/>'
    ),
    "award": (
        '<circle cx="12" cy="8" r="6"/>'
        '<path d="M15.477 12.89L17 22l-5-3-5 3 1.523-9.11"/>'
    ),
    "graduation-cap": (
        '<path d="M22 10v6M2 10l10-5 10 5-10 5z"/>'
        '<path d="M6 12v5c3 3 9 3 12 0v-5"/>'
    ),

    # ---- consulting ----
    "briefcase": (
        '<rect x="2" y="7" width="20" height="14" rx="2"/>'
        '<path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/>'
        '<line x1="12" y1="12" x2="12" y2="12.01"/>'
        '<path d="M2 12h20"/>'
    ),
    "target": (
        '<circle cx="12" cy="12" r="10"/>'
        '<circle cx="12" cy="12" r="6"/>'
        '<circle cx="12" cy="12" r="2"/>'
    ),
    "users": (
        '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>'
        '<circle cx="9" cy="7" r="4"/>'
        '<path d="M23 21v-2a4 4 0 0 0-3-3.87"/>'
        '<path d="M16 3.13a4 4 0 0 1 0 7.75"/>'
    ),
    "presentation": (
        '<path d="M2 3h20"/>'
        '<path d="M21 3v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V3"/>'
        '<path d="M7 21l5-5 5 5"/>'
    ),
    "chart-dots": (
        '<rect x="3" y="3" width="18" height="18" rx="2"/>'
        '<circle cx="8" cy="16" r="1.5" fill="currentColor" stroke="none"/>'
        '<circle cx="12" cy="10" r="1.5" fill="currentColor" stroke="none"/>'
        '<circle cx="16" cy="13" r="1.5" fill="currentColor" stroke="none"/>'
        '<polyline points="8 16 12 10 16 13"/>'
    ),

    # ---- fitness / sport ----
    "run": (
        '<circle cx="14" cy="4.5" r="1.5" fill="currentColor" stroke="none"/>'
        '<path d="M4.5 17.5l4.5-1.5 2-4"/>'
        '<path d="M15.5 20.5l-1-5.5-2-2.5 1.5-5.5"/>'
        '<path d="M7.5 13l2-4 4.5-0.5 4 2.5 3 0.5"/>'
    ),
    "trophy": (
        '<line x1="8" y1="21" x2="16" y2="21"/>'
        '<line x1="12" y1="17" x2="12" y2="21"/>'
        '<path d="M7 4h10l-1 7a5 5 0 0 1-8 0z"/>'
        '<path d="M5 9H3"/>'
        '<path d="M19 9h2"/>'
    ),
    "medal": (
        '<circle cx="12" cy="15" r="5"/>'
        '<path d="M8.5 7.5l-2.5-4.5h12l-2.5 4.5"/>'
        '<path d="M8.5 7.5q3.5 3 7 0"/>'
    ),
    "dumbbell": (
        '<circle cx="6" cy="7" r="2" fill="currentColor" stroke="none"/>'
        '<circle cx="6" cy="17" r="2" fill="currentColor" stroke="none"/>'
        '<circle cx="18" cy="7" r="2" fill="currentColor" stroke="none"/>'
        '<circle cx="18" cy="17" r="2" fill="currentColor" stroke="none"/>'
        '<line x1="6" y1="9" x2="6" y2="15"/>'
        '<line x1="18" y1="9" x2="18" y2="15"/>'
        '<line x1="7" y1="12" x2="17" y2="12"/>'
    ),
    "bike": (
        '<circle cx="5" cy="17" r="3"/>'
        '<circle cx="19" cy="17" r="3"/>'
        '<polyline points="5 17 11 9 11 17"/>'
        '<polyline points="11 9 16 9 19 17"/>'
        '<line x1="13" y1="6" x2="16" y2="9"/>'
        '<line x1="11" y1="6" x2="15" y2="6"/>'
    ),

    # ---- general / other ----
    "star": (
        '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 '
        '12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"'
        ' fill="currentColor" stroke="none"/>'
    ),
    "diamond": (
        '<path d="M2.7 10.3a2.41 2.41 0 0 0 0 3.41l7.56 7.57a2.41 2.41 0 0 0 3.4 0'
        'l7.57-7.57a2.41 2.41 0 0 0 0-3.41L13.66 2.72a2.41 2.41 0 0 0-3.41 0L2.7 10.3z"/>'
    ),
    "crown": (
        '<path d="M3 19l3-8 5.5 5 2.5-9 2.5 9 5.5-5 3 8H3z"/>'
        '<line x1="3" y1="19" x2="21" y2="19"/>'
    ),
    "rocket": (
        '<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91'
        'a2.18 2.18 0 0 0-2.91-.09z"/>'
        '<path d="M12 15l-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11'
        'a22.35 22.35 0 0 1-4 2z"/>'
        '<path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/>'
        '<path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>'
    ),
    "globe": (
        '<circle cx="12" cy="12" r="9"/>'
        '<line x1="3.6" y1="9" x2="20.4" y2="9"/>'
        '<line x1="3.6" y1="15" x2="20.4" y2="15"/>'
        '<path d="M11.5 3a17 17 0 0 0 0 18"/>'
        '<path d="M12.5 3a17 17 0 0 1 0 18"/>'
    ),
}

# ---------------------------------------------------------------------------
# Industry → icon pool
# ---------------------------------------------------------------------------

_INDUSTRY_ICONS: Dict[str, List[str]] = {
    "tech":       ["device-laptop", "cpu", "cloud", "code", "wifi", "layers", "bolt"],
    "healthcare": ["heart-pulse", "shield-check", "leaf", "activity", "stethoscope"],
    "finance":    ["trending-up", "coin", "building-bank", "chart-line", "wallet"],
    "food":       ["chef-hat", "coffee", "salad", "pizza", "apple"],
    "creative":   ["palette", "pencil", "brush", "stars", "wand"],
    "retail":     ["shopping-bag", "tag", "hanger", "shirt", "package"],
    "fitness":    ["run", "trophy", "medal", "dumbbell", "bike"],
    "education":  ["book-open", "school", "microscope", "award", "graduation-cap"],
    "consulting": ["briefcase", "target", "users", "presentation", "chart-dots"],
    "other":      ["star", "diamond", "crown", "rocket", "globe"],
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
    """SVG <g> that renders a named Tabler icon at (0,0) scaled to `size`×`size`."""
    inner = _ICONS.get(icon_name, _ICONS["star"])
    scale = size / 24.0
    return (
        f'<g transform="scale({scale:.4f})" color="{color}" '
        f'stroke="currentColor" stroke-width="2" stroke-linecap="round" '
        f'stroke-linejoin="round" fill="none">'
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
    cy = H * 0.28
    icon_x = cx - icon_size / 2
    icon_y = cy - icon_size / 2

    h_font = _load_font(font.heading_file)

    name_size = 30.0
    # Vertically center the name in the space below the icon
    name_y = cy + icon_size * 0.62 + (H - cy - icon_size * 0.62) * 0.52

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
    cy = H * 0.34
    icon_x = cx - icon_size / 2
    icon_y = cy - icon_size / 2

    h_font = _load_font(font.heading_file)

    name_size = 24.0
    # Vertically center the name in the space below the icon
    icon_bottom = cy + icon_size * 0.62
    name_y = icon_bottom + (H - icon_bottom) * 0.52

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

    name = (business_name.strip() or "Brand")[:60]
    seed = _make_seed(name)
    rng  = random.Random(seed)

    industry  = _detect_industry(business_type)
    icon_pool = _INDUSTRY_ICONS.get(industry, _INDUSTRY_ICONS["other"])

    base_color = _INDUSTRY_BASE_COLORS[industry]
    pref_colors = prefs.get("colors", [])
    if isinstance(pref_colors, list) and pref_colors:
        candidate = pref_colors[0]
        if isinstance(candidate, str) and candidate.startswith("#") and len(candidate) == 7:
            base_color = candidate.lower()

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
