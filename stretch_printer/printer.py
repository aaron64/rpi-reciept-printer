from pathlib import Path

RES_DIR = Path(__file__).parent / "res"

STRETCHES = {
    "Chest Stretch": "chest-stretch.png",
    "Figure 4 Stretch": "figure4-stretch.png",
    "Hip Flexor Stretch": "hip-flexor-stretch.png",
    "Lat Stretch": "lat-stretch.png",
    "Pancake Stretch": "pancake-stretch.png",
}

SEPARATOR = "-" * 42
CHECKBOX_LINE = "[ ] 30 Seconds   [ ] 30 Seconds"


def print_stretches(p):
    names = list(STRETCHES)
    for i, name in enumerate(names):
        p.image(str(RES_DIR / STRETCHES[name]), center=True)
        p.set(align="center", bold=True)
        p.text(name)
        p.set_with_default()
        p.text(CHECKBOX_LINE)

        if i < len(names) - 1:
            p.text(SEPARATOR)

    p.cut()
