TASK_DISP_LATE_WITHIN_DAYS = 3

UNFILED_TASKS_COUNT = 3


class ModuleTickTick:
    def __init__(self, config):
        pass

    def render(self, p, context):
        p.set(bold=True)
        p.text("Today's Tasks")
        p.set(bold=False)

        if context.ticktick_error:
            p.text(f"Tasks unavailable: {context.ticktick_error}")
            p.cut()
            return

        for project in context.projects:
            tasks_today = project.tasks_today()
            tasks_due = project.tasks_due_within_days(TASK_DISP_LATE_WITHIN_DAYS)

            if not (tasks_today or tasks_due):
                continue

            p.text(f"{project.name}:")
            for task in tasks_today:
                p.text(f"    [ ] {task.name}")
                for subtask in task.subtasks:
                    complete_mark = 'X' if subtask.complete else ' '
                    p.text(f"        [{complete_mark}] {subtask.name}")
                if task.subtask_overrun:
                    p.text(f"        {task.subtask_overrun} more items...")
            for task in tasks_due:
                due_str = f"{task.delta_days} " + ("day" if task.delta_days == -1 else "days")
                p.text(f"    [ ] ({due_str}) {task.name}")
                for subtask in task.subtasks:
                    complete_mark = 'X' if subtask.complete else ' '
                    p.text(f"        [{complete_mark}] {subtask.name}")
                if task.subtask_overrun:
                    p.text(f"        {task.subtask_overrun} more items...")

        # Add unfiled task placeholders for manual additions
        p.text("")
        for i in range(UNFILED_TASKS_COUNT):
            p.text("    [ ] _________________________")
        p.text("")

        reschedule_tasks = [task for project in context.projects for task in project.tasks_late(3)]
        if reschedule_tasks:
            p.text("Reschedule tasks:")
            for reschedule_task in reschedule_tasks:
                p.text(f"    - ({reschedule_task.delta_days} days) {reschedule_task.name}")

        p.cut()
