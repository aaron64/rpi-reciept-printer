import requests
import json
from datetime import datetime, timezone

def get_day_with_suffix(day):
    if 11 <= day <= 13:
        return f"{day}th"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(day%10, "th")
    return f"{day}{suffix}"

class ModuleHeader:
    def __init__(self, config):
        pass

    def reciept_print(self, p):
        today = datetime.today()
        p.set(bold=True, double_width=True, double_height=True)
        p.text(f"{today.strftime('%B')} {get_day_with_suffix(today.day)} {today.year}\n")
        p.set_with_default()
