import argparse
import configparser

from RecieptPrinter import RecieptPrinter
from stretch_printer.printer import print_stretches
from tasks_printer.context import build_context
from tasks_printer.printer import render_receipt
from workout_printer.printer import list_workouts, print_workouts, render_workout


def load_config():
    config = configparser.ConfigParser(interpolation=None)
    config.read("config.ini")
    return config


def run_daily(p):
    config = load_config()
    context = build_context(config)
    render_receipt(p, context, config)
    print_workouts(p, context)
    print_stretches(p)


def run_tasks_print(p):
    config = load_config()
    context = build_context(config)
    render_receipt(p, context, config)


def run_workout_list():
    for name in list_workouts():
        print(name)


def run_workout_print(p, name):
    rendered = render_workout(name)
    if rendered is None:
        print(f"Unknown workout '{name}'")
        return

    for line in rendered.splitlines():
        p.text(line)
    p.cut()


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry", action="store_true", help="Print to console only, skip the physical printer")
    subparsers = parser.add_subparsers(dest="command")

    workout_parser = subparsers.add_parser("workout")
    workout_subparsers = workout_parser.add_subparsers(dest="workout_command", required=True)
    workout_subparsers.add_parser("list")
    workout_print_parser = workout_subparsers.add_parser("print")
    workout_print_parser.add_argument("name")

    tasks_parser = subparsers.add_parser("tasks")
    tasks_subparsers = tasks_parser.add_subparsers(dest="tasks_command", required=True)
    tasks_subparsers.add_parser("print")

    return parser


def main():
    args = build_parser().parse_args()

    if args.command == "workout":
        if args.workout_command == "list":
            run_workout_list()
        elif args.workout_command == "print":
            run_workout_print(RecieptPrinter(dry=args.dry), args.name)
        return

    if args.command == "tasks":
        if args.tasks_command == "print":
            run_tasks_print(RecieptPrinter(dry=args.dry))
        return

    run_daily(RecieptPrinter(dry=args.dry))


if __name__ == "__main__":
    main()
