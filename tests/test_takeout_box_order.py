"""Dry-run check: Order validation and receipt rendering for the Takeout Box
order webhook printer.

Run with: python3 tests/test_takeout_box_order.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from RecieptPrinter import RecieptPrinter
from takeout_box_printer.models import Order, OrderValidationError
from takeout_box_printer.printer import render_order


def render_dry(order):
    printed_lines = []
    p = RecieptPrinter(dry=True)
    original_text = p.text

    def capture(string, *args, **kwargs):
        printed_lines.append(string)
        return original_text(string, *args, **kwargs)

    p.text = capture
    render_order(p, order)
    return "\n".join(printed_lines)


def test_valid_order_renders_items():
    order = Order.from_dict({
        "order_number": "1024",
        "order_name": "Jane Doe",
        "items": [
            {"name": "Takeout Box", "color": "red", "handedness": "standard"},
            {"name": "Takeout Box", "color": "blue", "handedness": "flipped"},
        ],
    })

    output = render_dry(order)

    assert "Order #1024" in output, "Expected order number in receipt"
    assert "Jane Doe" in output, "Expected order name in receipt"
    assert "Color: Red" in output, "Expected first item's color"
    assert "Handedness: Flipped" in output, "Expected second item's handedness"
    print("PASS: valid order renders order number, name, and both items")


def test_invalid_color_rejected():
    try:
        Order.from_dict({
            "order_number": "1025",
            "order_name": "John Smith",
            "items": [{"name": "Takeout Box", "color": "purple", "handedness": "standard"}],
        })
    except OrderValidationError:
        print("PASS: invalid color rejected")
        return
    raise AssertionError("Expected OrderValidationError for invalid color")


def test_invalid_handedness_rejected():
    try:
        Order.from_dict({
            "order_number": "1026",
            "order_name": "John Smith",
            "items": [{"name": "Takeout Box", "color": "red", "handedness": "sideways"}],
        })
    except OrderValidationError:
        print("PASS: invalid handedness rejected")
        return
    raise AssertionError("Expected OrderValidationError for invalid handedness")


def test_missing_items_rejected():
    try:
        Order.from_dict({"order_number": "1027", "order_name": "No Items", "items": []})
    except OrderValidationError:
        print("PASS: empty items list rejected")
        return
    raise AssertionError("Expected OrderValidationError for empty items")


def main():
    test_valid_order_renders_items()
    test_invalid_color_rejected()
    test_invalid_handedness_rejected()
    test_missing_items_rejected()


if __name__ == "__main__":
    main()
