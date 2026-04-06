import anthropic
from dotenv import load_dotenv
from agents import sports, finance, fitness
from agents.calendar_agent import run as calendar_run

load_dotenv()
client = anthropic.Anthropic()

def run_daily_brief():
    print("Starting agents...")

    print("Sports reporter working...")
    sports_report = sports.run()

    print("Financial reporter working...")
    finance_report = finance.run()

    print("Fitness coach working...")
    fitness_report = fitness.run()

    print("Calendar agent working...")
    calendar_report = calendar_run()

    print("Orchestrator composing brief...")

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1200,
        system="""You are a personal assistant.
        You receive reports from multiple agents and compose
        one organized daily brief in Hebrew.""",
        messages=[
            {
                "role": "user",
                "content": f"""
                Sports report:
                {sports_report}

                Financial report:
                {finance_report}

                Fitness report:
                {fitness_report}

                Calendar report:
                {calendar_report}

                Please compose one organized daily brief from these reports.
                """
            }
        ]
    )
    return response.content[0].text