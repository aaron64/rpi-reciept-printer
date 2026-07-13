from tasks_printer.printer import run as print_todays_tasks
from workout_printer.printer import print_workout

WORKOUT_TASK_PREFIX = "Workout - "


def main():
    todays_tasks = print_todays_tasks(dry=False)

    for task in todays_tasks:
        if not task.name.startswith(WORKOUT_TASK_PREFIX):
            continue
        workout_name = task.name[len(WORKOUT_TASK_PREFIX):].strip()
        if not print_workout(workout_name, dry=False):
            print(f"Unknown workout '{workout_name}' referenced by task '{task.name}'")


if __name__ == "__main__":
    main()
