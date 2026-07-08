"""Copy Phosphor fill icons into app/assets/icons/."""
import os
import shutil

ICONS = {
    # food
    "coffee":       "coffee",
    "pizza":        "pizza",
    "fork-knife":   "fork-knife",
    "bowl-food":    "bowl-food",
    "wine":         "wine",
    "cooking-pot":  "cooking-pot",
    # tech
    "cpu":          "cpu",
    "code":         "code",
    "cloud":        "cloud",
    "rocket":       "rocket",
    "circuitry":    "circuitry",
    # fitness
    "bicycle":           "bicycle",
    "person-simple-run": "person-simple-run",
    "trophy":            "trophy",
    "barbell":           "barbell",
    "medal":             "medal",
    # finance
    "currency-dollar": "currency-dollar",
    "chart-line-up":   "chart-line-up",
    "bank":            "bank",
    "coins":           "coins",
    "hand-coins":      "hand-coins",
    # healthcare
    "heart":        "heart",
    "first-aid-kit": "first-aid-kit",
    "stethoscope":  "stethoscope",
    "pill":         "pill",
    "dna":          "dna",
    # education
    "book-open":       "book-open",
    "graduation-cap":  "graduation-cap",
    "pencil":          "pencil",
    "chalkboard":      "chalkboard",
    "atom":            "atom",
    # creative
    "paint-brush": "paint-brush",
    "palette":     "palette",
    "camera":      "camera",
    "music-note":  "music-note",
    "pen-nib":     "pen-nib",
    # retail
    "shopping-bag": "shopping-bag",
    "tag":          "tag",
    "storefront":   "storefront",
    "coat-hanger":  "coat-hanger",
    "gift":         "gift",
    # consulting
    "briefcase":  "briefcase",
    "handshake":  "handshake",
    "chart-bar":  "chart-bar",
    "lightbulb":  "lightbulb",
    "users":      "users",
}

SRC = "node_modules/@phosphor-icons/core/assets/fill"
DST = "app/assets/icons"
os.makedirs(DST, exist_ok=True)

ok = 0
missing = []
for key, phosphor_name in ICONS.items():
    src = os.path.join(SRC, f"{phosphor_name}-fill.svg")
    dst = os.path.join(DST, f"{key}.svg")
    if os.path.exists(src):
        shutil.copy(src, dst)
        print(f"✓ {key}")
        ok += 1
    else:
        print(f"✗ NOT FOUND: {phosphor_name}-fill.svg")
        missing.append(key)

print(f"\n{ok} copied, {len(missing)} missing: {missing}")
