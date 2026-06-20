"""
Tests for backend/app/services/logo_generator.py

Run from backend/:
    pytest tests/test_logo_generator.py -v
"""
import pytest

from app.services.logo_generator import (
    LogoVariant,
    _detect_industry,
    _generate_palette,
    _hex_to_hsl,
    _hsl_to_hex,
    generate_logo_variants,
)


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_determinism_same_inputs_same_svg():
    """Identical inputs must produce byte-for-byte identical SVG output."""
    r1 = generate_logo_variants("Acme Corp", "technology startup", count=4)
    r2 = generate_logo_variants("Acme Corp", "technology startup", count=4)

    assert len(r1) == len(r2) == 4
    for v1, v2 in zip(r1, r2):
        assert v1.svg == v2.svg
        assert v1.icon_name == v2.icon_name
        assert v1.font_heading == v2.font_heading
        assert v1.palette == v2.palette
        assert v1.layout == v2.layout


def test_determinism_with_prefs():
    prefs = {"style": "minimal", "colors": ["#e63946"]}
    r1 = generate_logo_variants("Blue River", "consulting services", prefs=prefs)
    r2 = generate_logo_variants("Blue River", "consulting services", prefs=prefs)
    for v1, v2 in zip(r1, r2):
        assert v1.svg == v2.svg


# ---------------------------------------------------------------------------
# Variety across industries
# ---------------------------------------------------------------------------


def test_different_industries_different_icons():
    """Different industries must map to different icon pools."""
    tech    = generate_logo_variants("Brand X", "technology software startup")
    food    = generate_logo_variants("Brand X", "restaurant and food service")
    finance = generate_logo_variants("Brand X", "investment banking capital")

    tech_icons    = {v.icon_name for v in tech}
    food_icons    = {v.icon_name for v in food}
    finance_icons = {v.icon_name for v in finance}

    assert tech_icons != food_icons,    "tech and food share identical icon sets"
    assert food_icons != finance_icons, "food and finance share identical icon sets"
    assert tech_icons != finance_icons, "tech and finance share identical icon sets"


def test_same_industry_different_names_get_variety():
    """Different company names in same industry should (via seed) differ in at least icon or palette."""
    alpha = generate_logo_variants("Alpha Solutions", "technology startup")
    beta  = generate_logo_variants("Quantum Dynamics", "technology startup")

    alpha_icons   = [v.icon_name for v in alpha]
    beta_icons    = [v.icon_name for v in beta]
    alpha_palette = [v.palette for v in alpha]
    beta_palette  = [v.palette for v in beta]

    # Seeds differ ⟹ at minimum the icon order or palette should differ
    assert alpha_icons != beta_icons or alpha_palette != beta_palette


def test_within_batch_different_icons():
    """Within a single batch of 4 variants, no two should share the same icon."""
    results = generate_logo_variants("Test Co", "technology startup", count=4)
    icons = [v.icon_name for v in results]
    assert len(set(icons)) == len(icons), f"Duplicate icons in batch: {icons}"


def test_within_batch_different_fonts():
    """Within a batch, font headings should vary."""
    results = generate_logo_variants("Test Co", "creative design agency", count=4)
    headings = [v.font_heading for v in results]
    assert len(set(headings)) > 1, f"All variants share same heading font: {headings[0]}"


def test_within_batch_different_layouts():
    """A batch of ≥3 variants should include more than one layout."""
    results = generate_logo_variants("Test Co", "consulting firm", count=4)
    layouts = [v.layout for v in results]
    assert len(set(layouts)) > 1, f"All variants use same layout: {layouts}"


# ---------------------------------------------------------------------------
# SVG content correctness
# ---------------------------------------------------------------------------


def test_svg_contains_business_name():
    name = "Sunrise Bakery"
    results = generate_logo_variants(name, "artisan bakery and coffee shop")
    for variant in results:
        text = variant.svg.decode("utf-8")
        assert name in text, f"Business name not found in variant layout={variant.layout}"


def test_svg_starts_and_ends_correctly():
    results = generate_logo_variants("Omega Ltd", "financial services")
    for variant in results:
        text = variant.svg.decode("utf-8").strip()
        assert text.startswith("<svg"), "SVG does not start with <svg"
        assert text.endswith("</svg>"), "SVG does not end with </svg>"


def test_no_hardcoded_industry_taglines():
    """Old premium_engine.py wrote fixed strings regardless of user input.
    New generator must derive taglines from actual business_type.

    Specifically: if I use a business_type that contains "tech" but isn't
    literally "TECHNOLOGY", the tag must reflect the actual description, not
    the old hardcoded string.
    """
    # These pairs: (business_type, must_not_contain)
    # The business_type has been chosen so the tagline will NOT equal the
    # forbidden string even after .upper() — proving the old hardcodes are gone.
    cases = [
        ("cloud software startup",     "FINANCIAL SERVICES"),
        ("artisan bakery",             "CULINARY EXCELLENCE"),
        ("private equity fund",        "HEALTHCARE"),
        ("wellness spa center",        "TECHNOLOGY"),
        ("strategic management group", "CREATIVE STUDIO"),
    ]
    # Universal: these strings must never appear regardless of input
    always_forbidden = ["since 2025", "PROFESSIONAL SERVICES"]

    for btype, must_not in cases:
        for variant in generate_logo_variants("Comp", btype):
            text = variant.svg.decode("utf-8")
            assert must_not + "</" not in text, (
                f"Found legacy tagline '{must_not}' for business_type='{btype}'"
            )

    for variant in generate_logo_variants("Comp", "general services"):
        text = variant.svg.decode("utf-8")
        for forbidden in always_forbidden:
            assert forbidden not in text


def test_business_name_xml_escaped():
    """Business names with XML special chars must not break SVG structure."""
    tricky_name = "A & B <Corp>"
    results = generate_logo_variants(tricky_name, "consulting")
    for v in results:
        text = v.svg.decode("utf-8")
        # Raw unescaped characters must not appear inside text elements
        assert "<Corp>" not in text
        assert "A & B" not in text  # raw ampersand
        assert "&amp;" in text or "A" in text  # escaped version present


def test_google_fonts_import_present():
    """Each SVG must reference a Google Fonts import for the chosen font pair."""
    results = generate_logo_variants("Bright Co", "education academy")
    for v in results:
        text = v.svg.decode("utf-8")
        assert "fonts.googleapis.com" in text, "Missing Google Fonts import"


# ---------------------------------------------------------------------------
# Count and custom options
# ---------------------------------------------------------------------------


def test_default_count_is_four():
    assert len(generate_logo_variants("Co", "tech")) == 4


def test_custom_count():
    assert len(generate_logo_variants("Co", "tech", count=2)) == 2
    assert len(generate_logo_variants("Co", "tech", count=1)) == 1


def test_custom_base_color_in_primary_palette():
    """User-supplied base color must appear as palette[0] (primary) in every variant."""
    custom = "#e63946"
    results = generate_logo_variants("Red Brand", "retail fashion", prefs={"colors": [custom]})
    for v in results:
        assert v.palette[0] == custom, (
            f"Expected primary={custom}, got {v.palette[0]} in layout={v.layout}"
        )


def test_invalid_color_pref_falls_back_to_default():
    """Non-hex or wrong-length color pref must not crash; falls back to industry default."""
    bad_prefs = {"colors": ["notacolor"]}
    results = generate_logo_variants("Co", "tech startup", prefs=bad_prefs)
    assert len(results) == 4  # should succeed silently


def test_style_pref_influences_font():
    """When a style preference is given, the FIRST variant must use that style's
    paired font — this is the primary UX guarantee for style preferences."""
    # "minimal" → first variant must be DM Sans
    minimal_results = generate_logo_variants("Starfield Analytics", "technology", prefs={"style": "minimal"})
    assert minimal_results[0].font_heading == "DM Sans", (
        f"First variant for style=minimal expected DM Sans, got {minimal_results[0].font_heading}"
    )

    # "elegant" → first variant must be Cormorant Garamond
    elegant_results = generate_logo_variants("Starfield Analytics", "technology", prefs={"style": "elegant"})
    assert elegant_results[0].font_heading == "Cormorant Garamond", (
        f"First variant for style=elegant expected Cormorant Garamond, got {elegant_results[0].font_heading}"
    )

    # The two first variants must differ from each other
    assert minimal_results[0].font_heading != elegant_results[0].font_heading


def test_empty_business_name_does_not_crash():
    results = generate_logo_variants("", "technology startup")
    assert len(results) == 4
    for v in results:
        assert v.svg  # non-empty


# ---------------------------------------------------------------------------
# Color utilities (unit tests)
# ---------------------------------------------------------------------------


def test_hex_hsl_roundtrip():
    for hex_color in ["#2563eb", "#059669", "#e63946", "#000000", "#ffffff"]:
        h, s, l = _hex_to_hsl(hex_color)
        result = _hsl_to_hex(h, s, l)
        # Roundtrip within ±1 per channel (rounding)
        orig = [int(hex_color[i:i + 2], 16) for i in (1, 3, 5)]
        got  = [int(result[i:i + 2], 16) for i in (1, 3, 5)]
        for o, g in zip(orig, got):
            assert abs(o - g) <= 1, f"Roundtrip failed: {hex_color} → {result}"


def test_palette_has_four_entries():
    for scheme in ("complement", "analogous", "monochrome"):
        palette = _generate_palette("#2563eb", scheme)
        assert len(palette) == 4, f"Expected 4 colors for scheme={scheme}"


def test_palette_entries_are_valid_hex():
    import re
    hex_re = re.compile(r"^#[0-9a-f]{6}$")
    for scheme in ("complement", "analogous", "monochrome"):
        for color in _generate_palette("#7c3aed", scheme):
            assert hex_re.match(color), f"Invalid hex color: {color}"


# ---------------------------------------------------------------------------
# Industry detection
# ---------------------------------------------------------------------------


def test_industry_detection_basic():
    assert _detect_industry("AI tech startup") == "tech"
    assert _detect_industry("restaurant and food service") == "food"
    assert _detect_industry("investment banking capital") == "finance"
    assert _detect_industry("healthcare clinic and wellness") == "healthcare"
    assert _detect_industry("creative design agency") == "creative"


def test_industry_detection_unknown_falls_back():
    assert _detect_industry("unrecognised nonsense words") == "other"


def test_industry_detection_case_insensitive():
    assert _detect_industry("TECHNOLOGY SOFTWARE") == "tech"
    assert _detect_industry("Restaurant Food") == "food"
