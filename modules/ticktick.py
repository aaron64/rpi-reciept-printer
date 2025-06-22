import requests
import json
from datetime import datetime, timezone

API_GET_PROJECTS_URL = "https://api.ticktick.com/open/v1/project"
API_GET_TASKS_URL = "https://api.ticktick.com/open/v1/project/{}/data"

TASK_PROJECTS = {
    'Out of House': {
        'id': None,
        'tasks': []
    },
    'House': {
        'id': None,
        'tasks': []
    },
    'Computer': {
        'id': None,
        'tasks': []
    }   
}


class ModuleTickTick:
    def __init__(self, config):
        
        self.bearer_token = config['bearer_token']
        self.api_headers = {
            'Authorization': "Bearer {}".format(self.bearer_token),
            'cache-control': "no-cache",
            'Content-Type': 'application/json/'
        }

        self.get_projects_api()
        
        for project_name, task_project in TASK_PROJECTS.items():
            self.get_tasks(project_name, task_project)

    def get_projects_api(self):
        try:
            response = requests.request("GET", API_GET_PROJECTS_URL, headers=self.api_headers)

            if response.status_code == 200:
                projects_json = response.json()
                print(f"Fetched {len(projects_json)} projects")

                for project_json in projects_json:
                    project_name = project_json.get('name')
                    project_id = project_json.get('id')

                    if project_name in TASK_PROJECTS:
                        TASK_PROJECTS[project_name]['id'] = project_id
                        print(f"Mapped project {project_name} to ID {project_id}")

                for name, project_data in TASK_PROJECTS.items():
                    if project_data['id'] is None:
                        print(f"Project {name} not found in TickTick response")
                return True
            else:
                print(f"Failed to fetch projects: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching projects: {e}")
            return False
    
    def get_tasks(self, project_name, task_project):
        now = datetime.now()
        try:
            response = requests.request("GET", API_GET_TASKS_URL.format(task_project['id']), headers=self.api_headers)
            if response.status_code == 200:
                tasks_json = response.json()['tasks']
                for task_json in tasks_json:
                    if 'dueDate' not in task_json:
                        continue
                    due_date = datetime.strptime(task_json['dueDate'], "%Y-%m-%dT%H:%M:%S.%f%z")
                    if due_date.date() == now.date():
                        print(f"Task {task_json['title']} is due today")
                        task_project['tasks'].append(task_json['title'])
                return True
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching project: {e}")
            return False

    def reciept_print(self, p):
        p.set(bold=True)
        p.text("Today's Tasks\n")
        p.set(bold=False)
        for project_name, task_project in TASK_PROJECTS.items():
            if not task_project['tasks']:
                continue

            p.text(f"{project_name}:\n")
            for task in task_project['tasks']:
                p.text(f"\t[ ] {task}\n")

