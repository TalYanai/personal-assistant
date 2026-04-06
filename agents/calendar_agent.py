import anthropic
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

load_dotenv()
client = anthropic.Anthropic()

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "..", "credentials.json")
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "..", "token.json")

def get_calendar_service():
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
            auth_url, _ = flow.authorization_url(prompt="consent")
            print(f"\nOpen this URL in your browser:\n{auth_url}\n")
            code = input("Paste the authorization code here: ")
            flow.fetch_token(code=code)
            creds = flow.credentials

        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)

def get_today_events() -> list:
    service = get_calendar_service()

    now = datetime.utcnow()
    start_of_day = now.replace(hour=0, minute=0, second=0).isoformat() + "Z"
    end_of_day = now.replace(hour=23, minute=59, second=59).isoformat() + "Z"

    # Get all calendars
    calendars = service.calendarList().list().execute()
    
    all_events = []
    for calendar in calendars["items"]:
        try:
            events_result = service.events().list(
                calendarId=calendar["id"],
                timeMin=start_of_day,
                timeMax=end_of_day,
                singleEvents=True,
                orderBy="startTime"
            ).execute()
            
            events = events_result.get("items", [])
            for event in events:
                event["calendar_name"] = calendar["summary"]
                all_events.append(event)
        except Exception:
            pass  # Skip calendars we can't access

    # Sort all events by start time
    all_events.sort(key=lambda e: e["start"].get("dateTime", e["start"].get("date", "")))
    
    return all_events

def run(query: str = "") -> str:
    events = get_today_events()

    if not events:
        return "אין אירועים ביומן להיום."

    events_text = ""
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date", ""))
        if "T" in start:
            time_str = datetime.fromisoformat(start).strftime("%H:%M")
        else:
            time_str = "כל היום"

        title = event.get("summary", "ללא כותרת")
        events_text += f"- {time_str}: {title}\n"

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=400,
        system="""You are a personal schedule assistant.
        You receive today's calendar events and write a short daily schedule brief in Hebrew.
        Be concise and helpful.""",
        messages=[
            {
                "role": "user",
                "content": f"Here are today's calendar events:\n{events_text}\nWrite a short schedule brief in Hebrew."
            }
        ]
    )

    return response.content[0].text