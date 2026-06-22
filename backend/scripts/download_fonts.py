"""
backend/scripts/download_fonts.py

Downloads OFL-licensed woff2 font files used by logo_generator.py.
Run once after cloning the repository:

    cd backend
    python scripts/download_fonts.py

Source: fontsource CDN (cdn.jsdelivr.net) which hosts Google Fonts under the
SIL Open Font License 1.1, permitting use, embedding, and distribution in
commercial products.

fontTools (used by logo_generator.py) reads both .woff2 and .ttf files
natively when the `brotli` package is installed.
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

FONTS_DIR = Path(__file__).parent.parent / "app" / "assets" / "fonts"
CDN = "https://cdn.jsdelivr.net/npm"

# (local_filename, fontsource_package_name, weight)
FONTS: list[tuple[str, str, int]] = [
    ("Montserrat-SemiBold.woff2",          "montserrat",         600),
    ("OpenSans-Regular.woff2",             "open-sans",          400),
    ("PlayfairDisplay-Bold.woff2",         "playfair-display",   700),
    ("Lato-Regular.ttf",                   None,                 400),   # already present as TTF
    ("DMSans-SemiBold.woff2",              "dm-sans",            600),
    ("DMMono-Regular.woff2",               "dm-mono",            400),
    ("Nunito-Bold.woff2",                  "nunito",             700),
    ("Oswald-SemiBold.woff2",              "oswald",             600),
    ("SourceSans3-Regular.woff2",          "source-sans-3",      400),
    ("CormorantGaramond-SemiBold.woff2",   "cormorant-garamond", 600),
    ("Jost-Light.woff2",                   "jost",               300),
    ("SpaceGrotesk-SemiBold.woff2",        "space-grotesk",      600),
    ("Inter-Regular.woff2",                "inter",              400),
    ("Raleway-Bold.woff2",                 "raleway",            700),
    ("Mulish-Light.woff2",                 "mulish",             300),
]


def _woff2_url(pkg: str, weight: int) -> str:
    return f"{CDN}/@fontsource/{pkg}@5/files/{pkg}-latin-{weight}-normal.woff2"


def download_all(force: bool = False) -> None:
    FONTS_DIR.mkdir(parents=True, exist_ok=True)
    ok = skipped = failed = 0

    for filename, pkg, weight in FONTS:
        dest = FONTS_DIR / filename
        if dest.exists() and not force:
            print(f"  skip  {filename} (exists)")
            skipped += 1
            continue

        if pkg is None:
            print(f"  skip  {filename} (manual TTF — obtain separately)")
            skipped += 1
            continue

        url = _woff2_url(pkg, weight)
        print(f"  fetch {filename} ...", end=" ", flush=True)
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                data = resp.read()
            dest.write_bytes(data)
            print(f"OK ({len(data):,} bytes)")
            ok += 1
        except Exception as exc:
            print(f"FAILED: {exc}", file=sys.stderr)
            dest.unlink(missing_ok=True)
            failed += 1

    print(f"\n  {ok} downloaded, {skipped} skipped, {failed} failed")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    force = "--force" in sys.argv
    print(f"Downloading fonts → {FONTS_DIR}")
    download_all(force=force)
