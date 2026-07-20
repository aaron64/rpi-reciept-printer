from datetime import datetime

from ..jinja_env import env


def get_day_with_suffix(day):
    if 11 <= day <= 13:
        return f"{day}th"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return f"{day}{suffix}"


class ModuleHeader:
    def __init__(self, config):
        pass

    def render(self, p, context):
        today = datetime.today()
        rendered = env.get_template("header.jinja").render(
            month=today.strftime('%B'),
            day_with_suffix=get_day_with_suffix(today.day),
            year=today.year,
        ).rstrip("\n")
        p.set(bold=True, double_width=True, double_height=True)
        p.text(f"{rendered}\n")
        p.set_with_default()
