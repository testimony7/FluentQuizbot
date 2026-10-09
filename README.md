# FluentQuizbot

Your smart English learning companion for fun, interactive quizzes and better fluency.

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then paste your BotFather token into .env
python -m bot.main
```

## Environment variables
| Name | Where | Example |
|------|-------|---------|
| BOT_TOKEN | `.env` locally, Railway Variables in production | token from @BotFather |
| DATABASE_PATH | Railway Variables | `/data/fluentquiz.db` |
| DAILY_HOUR_UTC | optional | `8` |

## Deploy on Railway
1. Push this repo to GitHub (the `.env` file is git-ignored).
2. Railway: New Project > Deploy from GitHub repo.
3. Service > **Variables**: add `BOT_TOKEN` and `DATABASE_PATH=/data/fluentquiz.db`.
4. Service > **Volumes** (or right-click the service canvas > Volume): create a volume and mount it at `/data`.
5. Keep the service at **1 replica** (SQLite is single-writer).

## Add more questions
Edit `bot/data/questions.json`. Keep the question under 300 characters, each option under 100, and the explanation under 200 (Telegram limits).
