# Multi-Agent Personal Assistant

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Claude API](https://img.shields.io/badge/Claude_API-D4A017?style=flat&logo=anthropic&logoColor=white)](https://anthropic.com)
[![Telegram](https://img.shields.io/badge/Telegram_Bot-26A5E4?style=flat&logo=telegram&logoColor=white)](https://python-telegram-bot.org)
[![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Railway](https://img.shields.io/badge/Railway-0B0D0E?style=flat&logo=railway&logoColor=white)](https://railway.app)

A Python multi-agent assistant. Every morning at 08:00 it can send a personalized daily brief; during the day it answers natural-language questions via Telegram, routing each question to a specialized agent.

Built with the **Claude API** as the intelligence and orchestration layer.

---

## Architecture

```
                        ┌─────────────────────┐
                        │     Orchestrator     │
                        │   (Claude API core)  │
                        └──────────┬──────────┘
                                   │
          ┌────────────┬───────────┼───────────┬────────────┐
          ▼            ▼           ▼           ▼            ▼
    ┌──────────┐ ┌──────────┐ ┌────────┐ ┌─────────┐ ┌──────────┐
    │  Sports  │ │ Finance  │ │Fitness │ │Calendar │ │  Mailer  │
    │  Agent   │ │  Agent   │ │ Agent  │ │  Agent  │ │  Agent   │
    │(nba_api) │ │(yfinance)│ │ (JSON) │ │(Google) │ │ (Gmail)  │
    └──────────┘ └──────────┘ └────────┘ └─────────┘ └──────────┘
                                   │
                  ┌────────────────┴─────────────────┐
                  ▼                                   ▼
        ┌──────────────────┐               ┌──────────────────┐
        │   Daily Email    │               │   Telegram Bot   │
        │  (08:00 brief)   │               │  (Q&A on demand) │
        └──────────────────┘               └──────────────────┘
                                   │
                        ┌──────────▼──────────┐
                        │   Flask Dashboard   │
                        │  (status & logs)    │
                        └─────────────────────┘
```

---

## Features

| Agent | What It Does |
|-------|-------------|
| **Finance Agent** | Tracks a configurable stock watchlist with daily price changes |
| **Sports Agent** | Israeli NBA players (Deni Avdija, Ben Saraf, Danny Wolf) — last game stats |
| **Fitness Agent** | Reads a personalized weekly workout plan and generates a motivating daily coaching brief |
| **Calendar Agent** | Connects to Google Calendar API and summarizes today's events |
| **Mailer Agent** | Composes and sends the full morning brief via Gmail |

Additional capabilities:
- **Keyword routing** — Telegram messages are matched against Hebrew and English keyword lists, and only the relevant agent runs
- **Bilingual** — understands Hebrew and English
- **Deployment** — runs as a worker process (see `Procfile`); it ran on Railway for a period and is not running now

---

## Status

A personal, single-user project. It is not running now. Routing is a keyword list, not a model decision. There are no automated tests and no CI.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI / Orchestration | Claude API (`claude-opus-4-5`) |
| Bot Interface | python-telegram-bot v22 |
| Finance Data | yfinance |
| Sports Data | nba_api |
| Calendar | Google Calendar API (OAuth 2.0) |
| Email | Gmail SMTP (`smtplib`) |
| Scheduling | APScheduler |
| Web Dashboard | Flask |
| Deployment | Railway.app |

---

## Project Structure

```
personal-assistant/
├── telegram_bot.py        # Main entry — bot + scheduler
├── orchestrator.py        # Composes daily brief from all agents
├── mailer.py              # Sends brief via Gmail
├── main.py                # CLI entry for local testing
├── workoutProg.json       # Weekly workout plan
├── agents/
│   ├── sports.py          # NBA stats for Israeli players
│   ├── finance.py         # Stock market watchlist
│   ├── fitness.py         # Daily workout coaching
│   ├── calendar_agent.py  # Google Calendar integration
│   └── scheduler.py       # Scheduling utilities
├── web/
│   ├── app.py             # Flask dashboard
│   └── templates/index.html
├── requirements.txt
├── Procfile               # Railway deployment config
└── .gitignore
```

---

## How to Run

### 1. Clone and install

```bash
git clone https://github.com/TalYanai/personal-assistant.git
cd personal-assistant
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Create `.env`

```env
ANTHROPIC_API_KEY=your_anthropic_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
GMAIL_ADDRESS=your_gmail_address
GMAIL_APP_PASSWORD=your_gmail_app_password
GMAIL_RECIPIENT=recipient_email_address
```

### 3. Google Calendar OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → enable **Google Calendar API**
2. Create an OAuth 2.0 Client ID (Desktop App) → download as `credentials.json`
3. Run the app — a browser prompt will authorize access and generate `token.json`

### 4. Run locally

```bash
python telegram_bot.py
```

### 5. Deploy to Railway

1. Push to GitHub (`.env`, `credentials.json`, `token.json` are gitignored)
2. [railway.app](https://railway.app) → New Project → Deploy from GitHub repo
3. Add all `.env` variables in the Variables tab
4. Railway reads `Procfile` and runs the bot as a worker process

---

## Example Queries

| Query | Agent Invoked |
|-------|--------------|
| `How is SPY doing today?` | Finance |
| `What's my workout today?` | Fitness |
| `Do I have any meetings?` | Calendar |
| `מה קורה עם המניות?` | Finance |
| `מה האימון שלי?` | Fitness |

---

## Author

**Tal Yanai** — MIS Student, Ben-Gurion University  
GitHub: [@TalYanai](https://github.com/TalYanai)
