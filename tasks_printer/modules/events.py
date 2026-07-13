from data_handlers.ticktick_api import TickTickAPI
from data_handlers.google_calendar_api import GoogleCalendarAPI

# Display configuration
MIN_EVENTS_TO_SHOW = 4
EVENT_PROJECT_NAME = "Event"

class ModuleEvents:
    def __init__(self, config):
        self.all_events = []
        self.error_message = None
        
        try:
            # Google Calendar configuration
            self.google_calendar_id = config.get('google_calendar_id', 'primary')
            credentials_file = config.get('google_credentials_file', 'credentials.json')
            token_file = config.get('google_token_file', 'token.json')
            self.google_api = GoogleCalendarAPI(credentials_file, token_file)
            
            # TickTick configuration
            self.ticktick_bearer_token = config.get('ticktick_bearer_token', '')
            self.ticktick_api = TickTickAPI(self.ticktick_bearer_token)
            
            # Fetch events from both sources
            self.fetch_all_events()
        except Exception as e:
            self.error_message = f"Events setup error: {e}"
    
    
    def fetch_all_events(self):
        """Fetch events from both Google Calendar and TickTick"""
        # Fetch Google Calendar events
        google_events = self.google_api.get_events(
            calendar_id=self.google_calendar_id,
            days_ahead=7,
            max_results=50
        )
        
        if google_events:
            self.all_events.extend(google_events)
            print(f"Fetched {len(google_events)} Google Calendar events")
        else:
            print("Failed to fetch Google Calendar events")
        
        # Fetch TickTick events
        ticktick_events = self.ticktick_api.get_events_from_project(
            EVENT_PROJECT_NAME,
            days_ahead=7
        )
        
        self.all_events.extend(ticktick_events)
        print(f"Fetched {len(ticktick_events)} TickTick events")
    
    def get_combined_events(self):
        """Get combined and sorted list of all events"""
        self.all_events.sort(key=lambda event: event.start_time)
        
        # Determine how many events to show
        # Show either all events this week, or at least MIN_EVENTS_TO_SHOW
        events_to_show = max(len(self.all_events), MIN_EVENTS_TO_SHOW)
        
        return self.all_events[:events_to_show]
    
    def reciept_print(self, p):
        """Print events to receipt"""
        p.set(bold=True)
        p.text("Upcoming Events")
        p.set(bold=False)
        
        if self.error_message:
            p.text(f"Events unavailable: {self.error_message}")
            return
            
        events = self.get_combined_events()
        
        if not events:
            p.text("No upcoming events")
            return
        
        for event in events:
            date_str = event.format_date()
            time_str = event.format_time()
            
            if time_str == "All day":
                p.text(f"    {date_str}: {event.name}")
            else:
                p.text(f"    {date_str} {time_str}: {event.name}")