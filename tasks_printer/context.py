from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from zoneinfo import ZoneInfo

from .data_handlers.ical_calendar_api import fetch_todays_events
from .data_handlers.models import Event, Project
from .data_handlers.ticktick_api import TickTickAPI
from .data_handlers.weather_api import WeatherData, fetch_weather

PROJECT_FILTER = ['Out of House', 'House', 'Computer']
SUBTASK_DISP_MAX = 5
SUBTASK_DISP_IF_COMPLETE = False

TICKTICK_EVENTS_DAYS_AHEAD = 2


@dataclass
class DailyContext:
    projects: List[Project] = field(default_factory=list)
    ticktick_error: Optional[str] = None
    weather: Optional[WeatherData] = None
    weather_error: Optional[str] = None
    events: List[Event] = field(default_factory=list)
    events_errors: List[str] = field(default_factory=list)


def _parse_url_list(raw):
    return [url.strip() for url in raw.split(',') if url.strip()]


def _fetch_ticktick_events(bearer_token, project_name, timezone):
    """TickTick tasks (from `project_name`) that fall on today, in local time."""
    api = TickTickAPI(bearer_token)
    raw_events = api.get_events_from_project(project_name, days_ahead=TICKTICK_EVENTS_DAYS_AHEAD)

    tz = ZoneInfo(timezone)
    today = datetime.now(tz).date()
    return [e for e in raw_events if e.start_time.astimezone(tz).date() == today]


def build_context(config) -> DailyContext:
    context = DailyContext()

    ticktick_config = config['ModuleTickTick'] if 'ModuleTickTick' in config else {}
    ticktick_bearer_token = ticktick_config.get('bearer_token')
    if not ticktick_bearer_token:
        context.ticktick_error = "TickTick config missing bearer_token"
    else:
        try:
            api = TickTickAPI(ticktick_bearer_token)
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

    schedule_config = config['ModuleSchedule'] if 'ModuleSchedule' in config else {}
    schedule_timezone = schedule_config.get('timezone', 'America/Los_Angeles')
    ical_urls = _parse_url_list(schedule_config.get('ical_urls', ''))
    ticktick_event_project = schedule_config.get('ticktick_event_project')

    events = []

    if ical_urls:
        calendar_events, calendar_errors = fetch_todays_events(ical_urls, schedule_timezone)
        events.extend(calendar_events)
        context.events_errors.extend(calendar_errors)

    if ticktick_event_project:
        if not ticktick_bearer_token:
            context.events_errors.append("TickTick events configured but bearer_token is missing")
        else:
            try:
                events.extend(_fetch_ticktick_events(ticktick_bearer_token, ticktick_event_project, schedule_timezone))
            except Exception as e:
                context.events_errors.append(f"TickTick events error: {e}")

    if not ical_urls and not ticktick_event_project:
        context.events_errors.append("Schedule config missing ical_urls/ticktick_event_project")

    events.sort(key=lambda e: e.start_time)
    context.events = events

    return context
