import asyncio
import os
import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from orchestrator import run_daily_brief
from agents import finance, fitness
from agents.calendar_agent import run as calendar_run

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))

async def send_brief(context: ContextTypes.DEFAULT_TYPE):
    """Sends the daily brief automatically"""
    print("Sending daily brief to Telegram...")
    brief = run_daily_brief()
    await context.bot.send_message(chat_id=CHAT_ID, text=brief, parse_mode="Markdown")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Personal Assistant is ready! Ask me anything.")

def classify_question(question: str) -> str:
    """Returns the category of the question: finance, fitness, calendar, sports, or general."""
    q = question.lower()

    sports_keywords = ["ספורט", "כדורגל", "כדורסל", "nba", "fifa", "משחק", "קבוצה", "שחקן", "sport", "basketball", "football", "soccer", "nfl", "score"]
    finance_keywords = ["מניות", "שוק", "מסחר", "קריפטו", "ביטקוין", "דולר", "שקל", "השקעה", "stock", "finance", "crypto", "bitcoin", "market", "trading", "nasdaq", "s&p"]
    fitness_keywords = ["אימון", "כושר", "ריצה", "שרירים", "תזונה", "קלוריות", "workout", "fitness", "run", "gym", "exercise", "calories", "protein"]
    calendar_keywords = ["יומן", "לוז", "פגישה", "אירוע", "תזכורת", "calendar", "meeting", "schedule", "event", "reminder", "appointment"]

    if any(kw in q for kw in sports_keywords):
        return "sports"
    if any(kw in q for kw in finance_keywords):
        return "finance"
    if any(kw in q for kw in fitness_keywords):
        return "fitness"
    if any(kw in q for kw in calendar_keywords):
        return "calendar"
    return "general"


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles free text questions — only runs relevant agents."""
    question = update.message.text
    print(f"Question received: {question}")

    category = classify_question(question)
    print(f"Classified as: {category}")

    # Sports is unavailable on Railway (stats.nba.com blocks cloud IPs)
    if category == "sports":
        await update.message.reply_text(
            "נתוני ספורט זמינים רק בסיכום הבוקר היומי שנשלח ב-08:00. "
            "נסה לשאול אותי שאלה אחרת!"
        )
        return

    await update.message.reply_text("Thinking...")

    import anthropic
    client = anthropic.Anthropic()

    # Fetch only relevant data
    data_sections = {}
    if category == "finance":
        data_sections["Finance"] = finance.run()
    elif category == "fitness":
        data_sections["Fitness"] = fitness.run()
    elif category == "calendar":
        data_sections["Calendar"] = calendar_run()
    else:  # general — run finance + fitness, skip sports
        data_sections["Finance"] = finance.run()
        data_sections["Fitness"] = fitness.run()

    data_block = "\n".join(f"{k}: {v}" for k, v in data_sections.items())

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=600,
        system="""You are a personal assistant with access to real-time data.
        Answer the user's question in Hebrew based on the data provided.
        Be concise and helpful.""",
        messages=[
            {
                "role": "user",
                "content": f"""
                User question: {question}

                Available data:
                {data_block}

                Answer the question in Hebrew.
                """
            }
        ]
    )

    await update.message.reply_text(response.content[0].text, parse_mode="Markdown")

def main():
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Daily brief at 08:00
    app.job_queue.run_daily(
        send_brief,
        time=datetime.time(hour=8, minute=0),
        chat_id=CHAT_ID
    )

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()