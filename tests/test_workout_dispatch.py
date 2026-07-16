"""Dry-run check: a "Workout - {name}" task should trigger that workout's receipt.

Stubs the TickTick network call with a fake task and runs the real
build_context -> render_receipt pipeline (dry, so nothing touches the
physical printer). Run with: python3 tests/test_workout_dispatch.py
"""
import configparser
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tasks_printer.data_handlers.ticktick_api as ticktick_api_mod
from tasks_printer.data_handlers.models import Project, Task
from tasks_printer.context import build_context
from tasks_printer.printer import render_receipt
from RecieptPrinter import RecieptPrinter

WORKOUT_NAME = "lower-core"


def fake_get_tasks_from_projects(self, project_names, max_subtasks=5, show_completed_subtasks=False):
    project = Project(id="fake-project", name=project_names[0])
    project.tasks.append(Task(f"Workout - {WORKOUT_NAME}", due_date=datetime.now()))
    return [project]


def main():
    ticktick_api_mod.TickTickAPI.get_tasks_from_projects = fake_get_tasks_from_projects

    config = configparser.ConfigParser(interpolation=None)
    config.read_string("""
[ModuleTickTick]
bearer_token = fake-token
""")

    context = build_context(config)

    printed_lines = []
    p = RecieptPrinter(dry=True)
    original_text = p.text

    def capture(string, *args, **kwargs):
        printed_lines.append(string)
        return original_text(string, *args, **kwargs)

    p.text = capture

    render_receipt(p, context, config)

    output = "\n".join(printed_lines)
    assert f"Workout - {WORKOUT_NAME}" in output, "Expected the triggering task in Today's Tasks"
    assert "LOWER + CORE" in output, "Expected the lower-core workout receipt to have printed"

    print(f"PASS: 'Workout - {WORKOUT_NAME}' task correctly triggered the {WORKOUT_NAME} workout receipt")


if __name__ == "__main__":
    main()
