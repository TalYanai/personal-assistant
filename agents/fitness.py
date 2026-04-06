import anthropic
import json
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = anthropic.Anthropic()

PLAN_PATH = os.path.join(os.path.dirname(__file__), "..", "workoutProg.json")

def load_plan() -> dict:
    with open(PLAN_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_today_workout() -> dict:
    plan = load_plan()
    today = datetime.now().strftime("%A")  # Monday, Tuesday, etc.
    return plan["days"].get(today, {})

def run(query: str = "") -> str:
    workout = get_today_workout()
    today = datetime.now().strftime("%A")

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=600,
        system="""You are a professional running and fitness coach.
        You receive today's workout plan and write a motivating daily brief in Hebrew.
        Be specific, practical, and sound like a real personal coach.
        Include: what the goal is today, exactly what to do, and one coaching tip.""",
        messages=[
            {
                "role": "user",
                "content": f"""
                Today is {today}.
                Here is today's workout:
                {json.dumps(workout, ensure_ascii=False, indent=2)}

                Write a short coaching brief in Hebrew for this workout.
                """
            }
        ]
    )

    return response.content[0].text