"""Dry-run check: a "Workout - {name}" task OR calendar/TickTick event should
trigger that workout's receipt.

Stubs the TickTick network calls and runs the real
build_context -> render_receipt -> print_workouts pipeline, exactly as
main.py wires them together (dry, so nothing touches the physical printer).
Run with: python3 tests/test_workout_dispatch.py
"""
import configparser
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tasks_printer.data_handlers.ticktick_api as ticktick_api_mod
from tasks_printer.data_handlers.models import Event, Project, Task
from tasks_printer.context import build_context
from tasks_printer.printer import render_receipt
from workout_printer.printer import print_workouts
from RecieptPrinter import RecieptPrinter


def render_dry(config_text):
    config = configparser.ConfigParser(interpolation=None)
    config.read_string(config_text)

    context = build_context(config)

    printed_lines = []
    p = RecieptPrinter(dry=True)
    original_text = p.text

    def capture(string, *args, **kwargs):
        printed_lines.append(string)
        return original_text(string, *args, **kwargs)

    p.text = capture

    render_receipt(p, context, config)
    print_workouts(p, context)
    return "\n".join(printed_lines)


def test_task_triggered():
    workout_name = "lower-core"

    def fake_get_tasks_from_projects(self, project_names, max_subtasks=5, show_completed_subtasks=False):
        project = Project(id="fake-project", name=project_names[0])
        project.tasks.append(Task(f"Workout - {workout_name}", due_date=datetime.now()))
        return [project]

    ticktick_api_mod.TickTickAPI.get_tasks_from_projects = fake_get_tasks_from_projects

    output = render_dry("""
[ModuleTickTick]
bearer_token = fake-token
""")

    assert f"Workout - {workout_name}" in output, "Expected the triggering task in Today's Tasks"
    assert "LOWER + CORE" in output, "Expected the lower-core workout receipt to have printed"
    print(f"PASS: 'Workout - {workout_name}' task correctly triggered the {workout_name} workout receipt")


def test_event_triggered():
    workout_name = "upper-pull"

    def fake_get_tasks_from_projects(self, project_names, max_subtasks=5, show_completed_subtasks=False):
        return []

    def fake_get_events_from_project(self, project_name, days_ahead=7):
        assert project_name == "Event"
        return [Event(f"Workout - {workout_name}", datetime.now())]

    ticktick_api_mod.TickTickAPI.get_tasks_from_projects = fake_get_tasks_from_projects
    ticktick_api_mod.TickTickAPI.get_events_from_project = fake_get_events_from_project

    output = render_dry("""
[ModuleTickTick]
bearer_token = fake-token

[ModuleSchedule]
ticktick_event_project = Event
""")

    assert "UPPER (PULL)" in output, "Expected the upper-pull workout receipt to have printed"
    print(f"PASS: 'Workout - {workout_name}' calendar/TickTick event correctly triggered the {workout_name} workout receipt")


def main():
    test_task_triggered()
    test_event_triggered()


if __name__ == "__main__":
    main()
