import schedule
import time
from orchestrator import run_daily_brief
from mailer import send_daily_brief

def morning_brief():
    print("Running morning brief...")
    brief = run_daily_brief()
    send_daily_brief(brief)
    print("Done!")

# Schedule every day at 08:00
schedule.every().day.at("08:00").do(morning_brief)

print("Scheduler running... waiting for 08:00")

while True:
    schedule.run_pending()
    time.sleep(60)