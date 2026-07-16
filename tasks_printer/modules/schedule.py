DEFAULT_START_HOUR = 6
DEFAULT_END_HOUR = 23

BAR_CHAR = "#"


def format_hour_label(hour):
    period = "AM" if hour < 12 else "PM"
    display_hour = hour % 12 or 12
    return f"{display_hour:2d} {period}"


def _hour_position(dt):
    return dt.hour + dt.minute / 60


class ModuleSchedule:
    def __init__(self, config):
        self.start_hour = int(config.get('start_hour', DEFAULT_START_HOUR))
        self.end_hour = int(config.get('end_hour', DEFAULT_END_HOUR))

    def render(self, p, context):
        p.set(bold=True)
        p.text("Today's Schedule")
        p.set(bold=False)

        for error in context.events_errors:
            p.text(f"  {error}")

        all_day = [e for e in context.events if e.is_all_day]
        timed = [e for e in context.events if not e.is_all_day]

        for event in all_day:
            p.text(f"  (all day) {event.name}")

        if not timed:
            if not all_day and not context.events_errors:
                p.text("  No events today")
            return

        for hour in range(self.start_hour, self.end_hour + 1):
            slot_start = hour
            slot_end = hour + 1

            starting_here = [e for e in timed if e.start_time.hour == hour]
            ongoing = any(
                _hour_position(e.start_time) < slot_end and _hour_position(e.end_time) > slot_start
                for e in timed
            )

            marker = BAR_CHAR if (ongoing or starting_here) else " "
            names = "; ".join(e.name for e in starting_here)
            label = format_hour_label(hour)

            if names:
                p.text(f"{label} {marker} {names}")
            else:
                p.text(f"{label} {marker}")
