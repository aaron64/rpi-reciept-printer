from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

WORKOUTS_DIR = Path(__file__).parent / "workouts"
TEMPLATES_DIR = Path(__file__).parent / "templates"

WORKOUT_TASK_PREFIX = "Workout - "

env = Environment(
    loader=FileSystemLoader([str(WORKOUTS_DIR), str(TEMPLATES_DIR)]),
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True,
)


def get_day_with_suffix(day):
    if 11 <= day <= 13:
        return f"{day}th"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return f"{day}{suffix}"


def list_workouts():
    return sorted(p.stem for p in WORKOUTS_DIR.glob("*.jinja"))


def render_workout(name):
    if name not in list_workouts():
        return None

    today = datetime.today()
    date_str = f"{today.strftime('%B')} {get_day_with_suffix(today.day)} {today.year}"

    template = env.get_template(f"{name}.jinja")
    return template.render(date=date_str)


def _extract_workout_name(name):
    if name.startswith(WORKOUT_TASK_PREFIX):
        return name[len(WORKOUT_TASK_PREFIX):].strip()
    return None


def find_workout_names(context):
    """Scan a tasks_printer DailyContext (today's tasks + today's events) for
    "Workout - {name}" entries, from either source."""
    names = []

    for project in context.projects:
        for task in project.tasks_today():
            name = _extract_workout_name(task.name)
            if name and name not in names:
                names.append(name)

    for event in context.events:
        name = _extract_workout_name(event.name)
        if name and name not in names:
            names.append(name)

    return names


def print_workouts(p, context):
    """Check `context` for today's "Workout - {name}" tasks/events and print
    each matching workout as its own receipt."""
    for workout_name in find_workout_names(context):
        rendered = render_workout(workout_name)
        if rendered is None:
            print(f"Unknown workout '{workout_name}' referenced by a task/event")
            continue

        for line in rendered.splitlines():
            p.text(line)
        p.cut()
