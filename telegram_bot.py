import asyncio
import os
import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from orchestrator import run_daily_brief
from agents import sports, finance, fitness
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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles free text questions"""
    question = update.message.text
    print(f"Question received: {question}")

    await update.message.reply_text("Thinking...")

    import anthropic
    client = anthropic.Anthropic()

    sports_data = sports.run()
    finance_data = finance.run()
    fitness_data = fitness.run()
    calendar_data = calendar_run()

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
                Sports: {sports_data}
                Finance: {finance_data}
                Fitness: {fitness_data}
                Calendar: {calendar_data}

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