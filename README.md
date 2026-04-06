# 🤖 Multi-Agent Personal Assistant

A production-deployed AI assistant system that runs 24/7 in the cloud, delivering a personalized daily brief every morning and answering natural language questions via Telegram — in Hebrew.

Built with **Claude AI** as the intelligence layer, coordinating specialized agents that pull real-time data from finance markets, NBA stats, Google Calendar, and personal fitness plans.

---

## Architecture

```
                        ┌─────────────────────┐
                        │     Orchestrator     │
                        │   (Claude AI core)   │
                        └──────────┬──────────┘
                                   │
          ┌────────────┬───────────┼───────────┬────────────┐
          ▼            ▼           ▼           ▼            ▼
    ┌──────────┐ ┌──────────┐ ┌────────┐ ┌─────────┐ ┌──────────┐
    │  Sports  │ │ Finance  │ │Fitness │ │Calendar │ │  Mailer  │
    │  Agent   │ │  Agent   │ │ Agent  │ │  Agent  │ │  Agent   │
    │(nba_api) │ │(yfinance)│ │  (JSON)│ │(Google) │ │ (Gmail)  │
    └──────────┘ └──────────┘ └────────┘ └─────────┘ └──────────┘
                                   │
                  ┌────────────────┴─────────────────┐
                  ▼                                   ▼
        ┌──────────────────┐               ┌──────────────────┐
        │   📧 Daily Email  │               │  💬 Telegram Bot  │
        │  (08:00 morning  │               │ (Q&A on demand)  │
        │     brief)       │               │                  │
        └──────────────────┘               └──────────────────┘
```

---

## Features

- 🌅 **Daily Morning Brief** — Automated summary delivered every day at 08:00 covering markets, workouts, schedule, and NBA scores
- 📈 **Finance Agent** — Tracks a stock watchlist (configurable) with daily price changes
- 🏀 **Sports Agent** — Follows Israeli NBA players (Deni Avdija, Ben Saraf, Danny Wolf) with last-game stats
- 💪 **Fitness Agent** — Reads a personalized weekly workout plan and generates a motivating daily coaching brief
- 📅 **Calendar Agent** — Connects to Google Calendar and summarizes today's events across all calendars
- 💬 **Telegram Q&A** — Ask questions in natural language (Hebrew or English) and get instant AI-powered answers
- 🧠 **Smart Routing** — Classifies each question and runs only the relevant agent, avoiding unnecessary API calls
- ☁️ **Cloud Deployed** — Runs 24/7 on Railway.app with zero maintenance

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Intelligence | [Claude API](https://www.anthropic.com/) (`claude-opus-4-5`) |
| Bot Interface | [python-telegram-bot](https://python-telegram-bot.org/) v22 |
| Finance Data | [yfinance](https://github.com/ranaroussi/yfinance) |
| Sports Data | [nba_api](https://github.com/swar/nba_api) |
| Calendar | [Google Calendar API](https://developers.google.com/calendar) |
| Email | Gmail SMTP via `smtplib` |
| Scheduling | APScheduler (via python-telegram-bot job queue) |
| Web Dashboard | Flask |
| Deployment | [Railway.app](https://railway.app) |
| Config | python-dotenv |

---

## Project Structure

```
personal-assistant/
├── telegram_bot.py        # Main entry point — Telegram bot + scheduler
├── orchestrator.py        # Composes daily brief from all agent outputs
├── mailer.py              # Sends the daily brief via Gmail
├── main.py                # CLI entry point for local testing
├── workoutProg.json       # Weekly workout plan (personalized)
├── agents/
│   ├── __init__.py
│   ├── sports.py          # NBA stats for Israeli players
│   ├── finance.py         # Stock market watchlist
│   ├── fitness.py         # Daily workout coaching brief
│   ├── calendar_agent.py  # Google Calendar integration
│   └── scheduler.py       # Scheduling utilities
├── web/
│   ├── app.py             # Flask web dashboard
│   └── templates/
│       └── index.html
├── requirements.txt
├── Procfile               # Railway deployment config
└── .gitignore
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/TalYanai/personal-assistant.git
cd personal-assistant
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### 3. Create a `.env` file

Create a `.env` file in the project root with the following variables:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
GMAIL_ADDRESS=your_gmail_address
GMAIL_APP_PASSWORD=your_gmail_app_password
GMAIL_RECIPIENT=recipient_email_address
```

> ⚠️ Never commit this file. It is listed in `.gitignore`.

### 4. Google Calendar OAuth Setup

The calendar agent uses the Google Calendar API with OAuth 2.0.

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project → enable the **Google Calendar API**
3. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID** → Desktop App
4. Download the credentials file and save it as `credentials.json` in the project root
5. On first run, you will be prompted to authorize access in your browser — a `token.json` file will be created automatically

> Both `credentials.json` and `token.json` are excluded from git via `.gitignore`.

### 5. Telegram Bot Setup

1. Open Telegram and message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the prompts to get your **bot token**
3. Start a conversation with your new bot and get your **chat ID** by messaging [@userinfobot](https://t.me/userinfobot)
4. Add both values to your `.env` file

### 6. Run locally

```bash
python telegram_bot.py
```

The bot will start polling for messages. Open Telegram and send it a message to test.

---

## Deploy to Railway

1. Push your code to GitHub (sensitive files are gitignored)
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
3. Select this repository
4. In the **Variables** tab, add all keys from your `.env` file
5. Railway reads the `Procfile` and runs `python telegram_bot.py` as a worker process
6. Your bot is now live 24/7 ☁️

---

## Usage — What You Can Ask

The Telegram bot understands questions in both **Hebrew and English** and routes them to the correct agent automatically.

| Example Question | Agent Used |
|-----------------|-----------|
| `מה קורה עם המניות היום?` | Finance |
| `How is the S&P doing?` | Finance |
| `מה האימון שלי היום?` | Fitness |
| `What's my workout today?` | Fitness |
| `מה יש לי ביומן?` | Calendar |
| `Do I have any meetings today?` | Calendar |
| `How much did SPY go up?` | Finance |
| `תן לי סיכום כללי` | Finance + Fitness |

> **Note:** NBA sports data is only available in the daily morning brief (08:00), as the NBA API is blocked on cloud servers. Sports questions via Telegram will return a friendly message explaining this.

---

## Screenshots

> Coming soon — Telegram conversation examples and daily brief samples

---

## Author

**Tal Yanai**
MIS Student — Ben-Gurion University of the Negev

- GitHub: [@TalYanai](https://github.com/TalYanai)

---

## License

This project is for personal use and portfolio demonstration purposes.
