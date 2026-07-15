from dataclasses import dataclass, field
from typing import List, Optional

from .data_handlers.models import Project
from .data_handlers.ticktick_api import TickTickAPI
from .data_handlers.weather_api import WeatherData, fetch_weather

PROJECT_FILTER = ['Out of House', 'House', 'Computer']
SUBTASK_DISP_MAX = 5
SUBTASK_DISP_IF_COMPLETE = False


@dataclass
class DailyContext:
    projects: List[Project] = field(default_factory=list)
    ticktick_error: Optional[str] = None
    weather: Optional[WeatherData] = None
    weather_error: Optional[str] = None


def build_context(config) -> DailyContext:
    context = DailyContext()

    ticktick_config = config['ModuleTickTick'] if 'ModuleTickTick' in config else {}
    if 'bearer_token' not in ticktick_config:
        context.ticktick_error = "TickTick config missing bearer_token"
    else:
        try:
            api = TickTickAPI(ticktick_config['bearer_token'])
            context.projects = api.get_tasks_from_projects(
                PROJECT_FILTER,
                max_subtasks=SUBTASK_DISP_MAX,
                show_completed_subtasks=SUBTASK_DISP_IF_COMPLETE,
            )
        except Exception as e:
            context.ticktick_error = f"TickTick error: {e}"

    weather_config = config['ModuleWeather'] if 'ModuleWeather' in config else {}
    if 'latitude' not in weather_config or 'longitude' not in weather_config:
        context.weather_error = "Weather config missing latitude/longitude"
    else:
        try:
            context.weather = fetch_weather(
                weather_config['latitude'],
                weather_config['longitude'],
                weather_config.get('timezone', 'America/Los_Angeles'),
            )
        except Exception as e:
            context.weather_error = f"Weather data error: {e}"

    return context
