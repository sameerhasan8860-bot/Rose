# MASTER X

Free Telegram group management bot. This is the first development release; anti-spam, anti-raid, CAPTCHA, dashboard and advanced group settings are not implemented yet.

## Implemented foundation
- aiogram 3 polling bot: /start, /help, /id and /rules
- Reply-based moderation commands: /warn, /mute, /unmute, /ban and /unban
- Group-admin and bot-permission checks before moderation actions
- Async SQLAlchemy models for groups, group settings, warnings and filters
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

To moderate a member, reply to one of their messages with /warn, /mute, /unmute, /ban or /unban. Make the bot an administrator with the required Restrict Members permission.

Never commit .env or share your bot token. GitHub Actions is for CI/tests, not reliable 24/7 hosting. This is an early development build, not a finished feature-complete bot.
