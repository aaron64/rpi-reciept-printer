import random

COLORS = ("red", "blue", "orange", "green", "pink")
HANDEDNESS_OPTIONS = ("standard", "flipped")

NOTE_ADJECTIVES = ("no", "extra", "light")
NOTE_FOODS = ("pickles", "onion", "ketchup", "tomato", "kimchi")


class OrderValidationError(ValueError):
    pass


def random_note():
    return f"{random.choice(NOTE_ADJECTIVES)} {random.choice(NOTE_FOODS)}"


class OrderItem:
    def __init__(self, name, color, handedness, note=None):
        if not name:
            raise OrderValidationError("item name is required")
        if color not in COLORS:
            raise OrderValidationError(f"invalid color '{color}', must be one of {COLORS}")
        if handedness not in HANDEDNESS_OPTIONS:
            raise OrderValidationError(f"invalid handedness '{handedness}', must be one of {HANDEDNESS_OPTIONS}")

        self.name = name
        self.color = color
        self.handedness = handedness
        self.note = note or random_note()

    @classmethod
    def from_dict(cls, data):
        try:
            name = data["name"]
            color = data["color"]
            handedness = data["handedness"]
        except KeyError as e:
            raise OrderValidationError(f"item missing required field: {e.args[0]}")

        return cls(name=name, color=color, handedness=handedness)


class Order:
    def __init__(self, number, name, items):
        if not number:
            raise OrderValidationError("order_number is required")
        if not name:
            raise OrderValidationError("order_name is required")
        if not items:
            raise OrderValidationError("order must have at least one item")

        self.number = number
        self.name = name
        self.items = items

    @classmethod
    def from_dict(cls, data):
        try:
            number = data["order_number"]
            name = data["order_name"]
            items_data = data["items"]
        except KeyError as e:
            raise OrderValidationError(f"order missing required field: {e.args[0]}")

        if not isinstance(items_data, list):
            raise OrderValidationError("items must be a list")

        items = [OrderItem.from_dict(item) for item in items_data]
        return cls(number=number, name=name, items=items)
