from orchestrator import run_daily_brief
from mailer import send_daily_brief

if __name__ == "__main__":
    brief = run_daily_brief()
    print("\n" + "="*50)
    print("Daily Brief")
    print("="*50)
    print(brief)

    send_daily_brief(brief)