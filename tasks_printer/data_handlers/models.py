from datetime import datetime, timezone
from reciept_util import filter_emojis

class Event:
    def __init__(self, name, start_time, is_all_day=False):
        self.name = filter_emojis(name)
        self.start_time = start_time
        self.is_all_day = is_all_day
    
    def format_time(self):
        if self.is_all_day:
            return "All day"
        return self.start_time.strftime("%I:%M %p")
    
    def format_date(self):
        return self.start_time.strftime("%a %m/%d")

class Task:
    def __init__(self, name, due_date=None):
        self.name = filter_emojis(name)
        self.due_date = due_date
        self.delta_days = 0
        self.subtasks = []
        self.subtask_overrun = 0
        
        if due_date:
            now = datetime.now()
            self.delta_days = (self.due_date.date() - now.date()).days
    
    def due_today(self):
        return self.delta_days == 0

    def late_within(self, num):
        return -num <= self.delta_days < 0
        
    def later_than(self, num):
        return self.delta_days < (num * -1)

class Subtask:
    def __init__(self, name, complete=False):
        self.name = name
        self.complete = complete

class Project:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.tasks = []

    def tasks_today(self):
        return list(filter(lambda t: t.due_today(), self.tasks))
    
    def tasks_due_within_days(self, days):
        return list(filter(lambda t: t.late_within(days), self.tasks))
    
    def tasks_late(self, days):
        return list(filter(lambda t: t.later_than(days), self.tasks))
