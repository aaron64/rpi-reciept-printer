from datetime import datetime
from pathlib import Path

from jinja2 import Template

WORKOUTS_DIR = Path(__file__).parent / "workouts"


def get_day_with_suffix(day):
    if 11 <= day <= 13:
        return f"{day}th"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return f"{day}{suffix}"


def list_workouts():
    return sorted(p.stem for p in WORKOUTS_DIR.glob("*.txt"))


def render_workout(name):
    workout_path = WORKOUTS_DIR / f"{name}.txt"
    if not workout_path.exists():
        return None

    today = datetime.today()
    date_str = f"{today.strftime('%B')} {get_day_with_suffix(today.day)} {today.year}"

    template = Template(workout_path.read_text())
    return template.render(date=date_str)
