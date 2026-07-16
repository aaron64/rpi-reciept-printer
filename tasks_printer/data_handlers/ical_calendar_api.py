from datetime import datetime, time
from zoneinfo import ZoneInfo

import icalendar
import recurring_ical_events
import requests

from .models import Event


def _to_local(dt, tz):
    if isinstance(dt, datetime):
        if dt.tzinfo is not None:
            return dt.astimezone(tz)
        return dt.replace(tzinfo=tz)
    return datetime.combine(dt, time.min, tzinfo=tz)


def _fetch_calendar_events(ical_url, tz, range_start, range_end):
    response = requests.get(ical_url)
    response.raise_for_status()

    calendar = icalendar.Calendar.from_ical(response.text)
    occurrences = recurring_ical_events.of(calendar).between(range_start, range_end)

    events = []
    for component in occurrences:
        name = str(component.get('SUMMARY', 'Untitled'))
        dtstart = component['DTSTART'].dt
        is_all_day = not isinstance(dtstart, datetime)
        dtend = component['DTEND'].dt if 'DTEND' in component else dtstart

        events.append(Event(
            name,
            _to_local(dtstart, tz),
            end_time=_to_local(dtend, tz),
            is_all_day=is_all_day,
        ))
    return events


def fetch_todays_events(ical_urls, timezone='America/Los_Angeles'):
    """Fetch today's events from one or more secret iCal URLs.

    Each URL is fetched independently so one broken/unreachable calendar
    doesn't prevent the others from showing up; failures are collected
    and returned alongside whatever events did come back.
    """
    tz = ZoneInfo(timezone)
    today = datetime.now(tz).date()
    range_start = datetime.combine(today, time.min, tzinfo=tz)
    range_end = datetime.combine(today, time.max, tzinfo=tz)

    events = []
    errors = []
    for ical_url in ical_urls:
        try:
            events.extend(_fetch_calendar_events(ical_url, tz, range_start, range_end))
        except Exception as e:
            errors.append(f"Calendar fetch failed: {e}")

    events.sort(key=lambda e: e.start_time)
    return events, errors
