from workout_printer.printer import render_workout

WORKOUT_TASK_PREFIX = "Workout - "


def find_workout_names(projects):
    names = []
    for project in projects:
        for task in project.tasks_today():
            if task.name.startswith(WORKOUT_TASK_PREFIX):
                names.append(task.name[len(WORKOUT_TASK_PREFIX):].strip())
    return names


class ModuleWorkout:
    def __init__(self, config):
        pass

    def render(self, p, context):
        for workout_name in find_workout_names(context.projects):
            rendered = render_workout(workout_name)
            if rendered is None:
                print(f"Unknown workout '{workout_name}' referenced by task")
                continue

            for line in rendered.splitlines():
                p.text(line)
            p.cut()
