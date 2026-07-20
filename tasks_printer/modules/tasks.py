import random

from ..jinja_env import env

TASK_DISP_LATE_WITHIN_DAYS = 3

UNFILED_TASKS_COUNT = 3

RESCHEDULE_TASKS_COUNT = 5


class ModuleTickTick:
    def __init__(self, config):
        pass

    def render(self, p, context):
        p.set(bold=True)
        p.text("Today's Tasks")
        p.set(bold=False)

        reschedule_tasks = [task for project in context.projects for task in project.tasks_late(3)]
        reschedule_sample = random.sample(reschedule_tasks, min(RESCHEDULE_TASKS_COUNT, len(reschedule_tasks)))

        rendered = env.get_template("tasks.jinja").render(
            error=context.ticktick_error,
            projects=context.projects,
            late_within_days=TASK_DISP_LATE_WITHIN_DAYS,
            unfiled_tasks_count=UNFILED_TASKS_COUNT,
            reschedule_sample=reschedule_sample,
        )

        for line in rendered.splitlines():
            p.text(line)

        p.cut()
