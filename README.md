# MASTER X

Free Telegram group management bot. This repository currently contains the initial working foundation; advanced moderation and dashboard modules are planned, not yet complete.

## Current foundation
- aiogram 3 polling bot with /start, /help, /id and /rules
- Async SQLAlchemy models for groups, settings, warnings and filters
- FastAPI health endpoint at /health
- Environment-based configuration
- GitHub Actions compile and pytest checks

## Setup
1. Create a Telegram bot with BotFather and copy its token.
2. Copy .env.example to .env.
3. Set BOT_TOKEN and GLOBAL_OWNER_ID in .env.
4. Install dependencies: pip install -r requirements.txt
5. Run the bot: python -m app.bot
6. Optional API: uvicorn app.api:app --host 0.0.0.0 --port 8000

Never commit .env or share your bot token. Add the bot to each group as an administrator and grant only the permissions it needs.

GitHub Actions is for CI/tests, not reliable 24/7 hosting. This is an early scaffold, not a finished feature-complete bot.
