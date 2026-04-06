import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
GMAIL_RECIPIENT = os.getenv("GMAIL_RECIPIENT")

def send_daily_brief(brief_text: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "הבריף היומי שלך"
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = GMAIL_RECIPIENT

    # Plain text version
    text_part = MIMEText(brief_text, "plain", "utf-8")
    msg.attach(text_part)

    print("Sending email...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, GMAIL_RECIPIENT, msg.as_string())

    print(f"Email sent to {GMAIL_RECIPIENT}")