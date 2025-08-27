import requests
import json
from datetime import datetime, timezone, timedelta
from .models import Event, Task, Subtask, Project

API_GET_PROJECTS_URL = "https://api.ticktick.com/open/v1/project"
API_GET_TASKS_URL = "https://api.ticktick.com/open/v1/project/{}/data"

class TickTickAPI:
    def __init__(self, bearer_token):
        self.bearer_token = bearer_token
        self.api_headers = {
            'Authorization': f"Bearer {bearer_token}",
            'cache-control': "no-cache",
            'Content-Type': 'application/json/'
        }
    
    def get_projects(self):
        """Fetch all projects from TickTick API"""
        try:
            response = requests.get(API_GET_PROJECTS_URL, headers=self.api_headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to fetch projects: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching projects: {e}")
            return None
    
    def get_project_tasks(self, project_id):
        """Fetch tasks for a specific project"""
        try:
            response = requests.get(API_GET_TASKS_URL.format(project_id), headers=self.api_headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to fetch tasks for project {project_id}: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Network error fetching tasks for project {project_id}: {e}")
            return None
    
    def find_project_by_name(self, project_name):
        """Find a project by name and return its ID"""
        projects = self.get_projects()
        if not projects:
            return None
        
        for project in projects:
            if project.get('name') == project_name:
                return project.get('id')
        
        return None
    
    def get_events_from_project(self, project_name, days_ahead=7):
        """Get events from a TickTick project as Event objects"""
        project_id = self.find_project_by_name(project_name)
        if not project_id:
            print(f"TickTick project '{project_name}' not found")
            return []
        
        project_data = self.get_project_tasks(project_id)
        if not project_data:
            return []
        
        tasks = project_data.get('tasks', [])
        events = []
        now = datetime.now(timezone.utc)
        time_max = now + timedelta(days=days_ahead)
        
        for task_json in tasks:
            try:
                name = task_json['title']
                
                if 'dueDate' in task_json:
                    start_time = datetime.strptime(task_json['dueDate'], "%Y-%m-%dT%H:%M:%S.%f%z")
                else:
                    # If no due date, assume it's for today
                    start_time = datetime.now(timezone.utc)
                
                # Only include events within the time range
                if now <= start_time <= time_max:
                    event = Event(name, start_time, is_all_day=True)
                    events.append(event)
            except Exception as e:
                print(f"Error parsing TickTick event: {e}")
        
        return events
    
    def get_tasks_from_projects(self, project_names, max_subtasks=5, show_completed_subtasks=False):
        """Get tasks from multiple TickTick projects as Task objects"""
        projects = []
        
        for project_name in project_names:
            project_id = self.find_project_by_name(project_name)
            if not project_id:
                print(f"TickTick project '{project_name}' not found")
                continue
            
            project = Project(project_id, project_name)
            project_data = self.get_project_tasks(project_id)
            
            if project_data:
                tasks_json = project_data.get('tasks', [])
                for task_json in tasks_json:
                    if 'dueDate' not in task_json:
                        continue
                    
                    try:
                        name = task_json['title']
                        due_date = datetime.strptime(task_json['dueDate'], "%Y-%m-%dT%H:%M:%S.%f%z")
                        task = Task(name, due_date)
                        
                        # Handle subtasks
                        if 'items' in task_json:
                            for subtask_json in task_json['items']:
                                subtask = Subtask(
                                    subtask_json['title'],
                                    subtask_json['status']
                                )
                                if subtask.complete:
                                    if show_completed_subtasks:
                                        task.subtasks.append(subtask)
                                else:
                                    task.subtasks.insert(0, subtask)
                            
                            if len(task.subtasks) > max_subtasks:
                                task.subtask_overrun = len(task.subtasks) - max_subtasks
                                task.subtasks = task.subtasks[:max_subtasks]
                        
                        project.tasks.append(task)
                    except Exception as e:
                        print(f"Error parsing TickTick task: {e}")
            
            projects.append(project)
        
        return projects
