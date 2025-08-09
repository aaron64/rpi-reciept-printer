from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from .models import Event

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class GoogleCalendarAPI:
    def __init__(self, credentials_file='credentials.json', token_file='token.json'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
    
    def authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        
        # Load existing token
        try:
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        except:
            pass
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Google Calendar authentication failed: {e}")
                    return False
            
            # Save the credentials for the next run
            try:
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"Failed to save Google credentials: {e}")
        
        self.service = build('calendar', 'v3', credentials=creds)
        return True
    
    def get_events(self, calendar_id='primary', days_ahead=7, max_results=50):
        """Get events from Google Calendar for the specified number of days ahead"""
        if not self.service:
            if not self.authenticate():
                return None
        
        try:
            # Get events for the specified time range
            now = datetime.utcnow().isoformat() + 'Z'
            time_max = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=now,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            raw_events = events_result.get('items', [])
            events = []
            
            for event_json in raw_events:
                try:
                    name = event_json.get('summary', 'Untitled Event')
                    
                    # Handle different datetime formats (all-day vs timed events)
                    start = event_json.get('start', {})
                    if 'dateTime' in start:
                        start_time = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
                        is_all_day = False
                    elif 'date' in start:
                        # All-day event
                        start_time = datetime.strptime(start['date'], '%Y-%m-%d').replace(tzinfo=timezone.utc)
                        is_all_day = True
                    else:
                        start_time = datetime.now(timezone.utc)
                        is_all_day = False
                    
                    event = Event(name, start_time, is_all_day)
                    events.append(event)
                except Exception as e:
                    print(f"Error parsing Google event: {e}")
            
            return events
            
        except Exception as e:
            print(f"Error fetching Google Calendar events: {e}")
            return None