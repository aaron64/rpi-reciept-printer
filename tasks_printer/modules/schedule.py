import math

from RecieptPrinter import CHAR_WIDTH

DEFAULT_START_HOUR = 6
DEFAULT_END_HOUR = 23

HOUR_LABEL_WIDTH = 2
COLUMN_SPACER = " "


def format_hour_label(hour):
    return f"{hour:02d}"


def _hour_position(dt):
    return dt.hour + dt.minute / 60


def _assign_columns(events):
    """Greedy interval-graph coloring: overlapping events get different columns."""
    columns_last_end = []
    assignments = {}
    for event in sorted(events, key=lambda e: e.start_time):
        placed = False
        for i, last_end in enumerate(columns_last_end):
            if event.start_time >= last_end:
                columns_last_end[i] = event.end_time
                assignments[event] = i
                placed = True
                break
        if not placed:
            columns_last_end.append(event.end_time)
            assignments[event] = len(columns_last_end) - 1
    return assignments, max(len(columns_last_end), 1)


def _render_cell(width, event, is_top, is_bottom):
    if event is None or width <= 0:
        return " " * width
    if width < 2:
        return ("+" if (is_top or is_bottom) else "|") * width

    if is_top:
        inner_width = width - 2
        name = event.name[:inner_width]
        content = name + "-" * (inner_width - len(name))
        return f"+{content}+"
    if is_bottom:
        return "+" + "-" * (width - 2) + "+"
    return "|" + " " * (width - 2) + "|"


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

        columns, num_columns = _assign_columns(timed)

        grid_width = CHAR_WIDTH - HOUR_LABEL_WIDTH - len(COLUMN_SPACER)
        grid_width -= len(COLUMN_SPACER) * (num_columns - 1)
        col_width = max(1, grid_width // num_columns)

        # First/last displayed row for each event, clipped to the graph's hour range.
        spans = {}
        for event in timed:
            first_hour = max(event.start_time.hour, self.start_hour)
            last_hour = max(math.ceil(_hour_position(event.end_time)) - 1, first_hour)
            last_hour = min(last_hour, self.end_hour)
            spans[event] = (first_hour, last_hour)

        for hour in range(self.start_hour, self.end_hour + 1):
            slot_start = hour
            slot_end = hour + 1

            cells = [" " * col_width] * num_columns
            for event in timed:
                if not (_hour_position(event.start_time) < slot_end and _hour_position(event.end_time) > slot_start):
                    continue
                first_hour, last_hour = spans[event]
                is_top = hour == first_hour
                is_bottom = hour == last_hour and not is_top
                cells[columns[event]] = _render_cell(col_width, event, is_top, is_bottom)

            label = format_hour_label(hour)
            p.text(f"{label}{COLUMN_SPACER}{COLUMN_SPACER.join(cells)}")
