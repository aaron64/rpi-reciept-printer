import requests
import json
from datetime import datetime, timezone

from reciept_util import filter_emojis 

API_GET_PROJECTS_URL = "https://api.ticktick.com/open/v1/project"
API_GET_TASKS_URL = "https://api.ticktick.com/open/v1/project/{}/data"

SUBTASK_DISP_IF_COMPLETE = False
SUBTASK_DISP_MAX = 5

TASK_DISP_LATE_WITHIN_DAYS = 3

TASK_PROJECTS = []

PROJECT_FILTER = ['Out of House', 'House', 'Computer']

RESCHEDULE_TASKS = []

class TickTickProject:
    def __init__(self, project_json):
        self.id = project_json.get('id')
        self.name = project_json.get('name')
        self.tasks = []

    def tasks_today(self):
        return list(filter(lambda t: t.due_today(), self.tasks))
    
    def tasks_due_within_days(self):
        return list(filter(lambda t: t.late_within(TASK_DISP_LATE_WITHIN_DAYS), self.tasks))
    
    def tasks_late(self):
        return list(filter(lambda t: t.later_than(TASK_DISP_LATE_WITHIN_DAYS), self.tasks))

class TickTickTask:
    def __init__(self, task_json):
        now = datetime.now()

        self.name = filter_emojis(task_json['title'])
        self.due_date = datetime.strptime(task_json['dueDate'], "%Y-%m-%dT%H:%M:%S.%f%z")
        self.delta_days = (self.due_date.date() - now.date()).days

        self.subtasks = []
        self.subtask_overrun = 0
        if 'items' in task_json:
            for subtask_json in task_json['items']:
                subtask = TickTickSubtask(subtask_json)
                if subtask.complete:
                    if SUBTASK_DISP_IF_COMPLETE:
                        self.subtasks.append(subtask)
                else:
                    self.subtasks.insert(0, subtask)
            if len(self.subtasks) > SUBTASK_DISP_MAX:
                self.subtask_overrun = len(self.subtasks) - SUBTASK_DISP_MAX
                self.subtasks = self.subtasks[:SUBTASK_DISP_MAX]

    def due_today(self):
        return self.delta_days == 0

    def late_within(self, num):
        return -num <= self.delta_days < 0
        
    def later_than(self, num):
        return self.delta_days < (num *-1)

class TickTickSubtask:
    def __init__(self, subtask_json):
        self.name = subtask_json['title']
        self.complete = subtask_json['status']

class ModuleTickTick:
    def __init__(self, config):
        
        self.bearer_token = config['bearer_token']
        self.api_headers = {
            'Authorization': "Bearer {}".format(self.bearer_token),
            'cache-control': "no-cache",
            'Content-Type': 'application/json/'
        }

        self.get_projects_api()
        
        for project in TASK_PROJECTS:
            self.get_tasks(project)

    def get_projects_api(self):
        try:
            response = requests.request("GET", API_GET_PROJECTS_URL, headers=self.api_headers)

            if response.status_code == 200:
                projects_json = response.json()
                print(f"Fetched {len(projects_json)} projects")

                for project_json in projects_json:
                    if project_json.get('name') in PROJECT_FILTER:
                        project = TickTickProject(project_json)
                        TASK_PROJECTS.append(project)
                        PROJECT_FILTER.remove(project.name)
                        print(f"Mapped project {project.name} to ID {project.id}")

                for missing_project_name in PROJECT_FILTER:
                    print(f"Project {missing_project_name} not found in TickTick response")
                return True
            else:
                print(f"Failed to fetch projects: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching projects: {e}")
            return False
    
    def get_tasks(self, project):
        try:
            response = requests.request("GET", API_GET_TASKS_URL.format(project.id), headers=self.api_headers)
            if response.status_code == 200:
                tasks_json = response.json()['tasks']
                for task_json in tasks_json:
                    if 'dueDate' not in task_json:
                        continue
                    task = TickTickTask(task_json)        
                    project.tasks.append(task)
                return True
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching project: {e}")
            return False

    def reciept_print(self, p):
        p.set(bold=True)
        p.text("Today's Tasks")
        p.set(bold=False)

        for project in TASK_PROJECTS:
            if not (project.tasks_today() or project.tasks_due_within_days()):
                continue

            p.text(f"{project.name}:")
            for task in project.tasks_today():
                p.text(f"    [ ] {task.name}")
                for subtask in task.subtasks:
                    complete_mark = 'X' if subtask.complete else ' '
                    p.text(f"        [{complete_mark}] {subtask.name}")
                if task.subtask_overrun:
                    p.text(f"        {task.subtask_overrun} more items...")
            for task in project.tasks_due_within_days():
                due_str = f"{task.delta_days} " + ("day" if task.delta_days == -1 else "days")
                p.text(f"    [ ] ({due_str}) {task.name}")
                for subtask in task.subtasks:
                    complete_mark = 'X' if subtask.complete else ' '
                    p.text(f"        [{complete_mark}] {subtask.name}")
                if task.subtask_overrun:
                    p.text(f"        {task.subtask_overrun} more items...")
                

        reschedule_tasks = [task for project in TASK_PROJECTS for task in project.tasks if task.later_than(3)]
        if reschedule_tasks:
            p.text("Reschedule tasks:")
            for reschedule_task in reschedule_tasks:
                p.text(f"    - ({reschedule_task.delta_days} days) {reschedule_task.name}")
