from pathlib import Path

from reciept_util import filter_emojis

RES_DIR = Path(__file__).parent / "res"
LOGO_PATH = RES_DIR / "rally-audio-header.bmp"
QR_PATH = RES_DIR / "qr.bmp"

SEPARATOR = "-" * 42


def render_order(p, order):
    if LOGO_PATH.exists():
        p.image(str(LOGO_PATH), center=True)

    p.set(align="center", bold=True, double_width=True, double_height=True)
    p.text(f"Order #{order.number}")
    p.set_with_default()

    p.set(align="center", bold=True)
    p.text(filter_emojis(order.name))
    p.set_with_default()

    p.text(SEPARATOR)

    for i, item in enumerate(order.items, start=1):
        p.set(bold=True)
        p.text(f"{i}) {filter_emojis(item.name)}")
        p.set_with_default()
        p.text(f"   Color: {item.color.capitalize()}")
        p.text(f"   Handedness: {item.handedness.capitalize()}")
        p.text(f'   "{item.note.capitalize()}"')

        if i < len(order.items):
            p.text(SEPARATOR)

    p.text(SEPARATOR)

    if QR_PATH.exists():
        p.image(str(QR_PATH), center=True)

    p.cut()
