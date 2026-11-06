# MASTER X

A free, modular Telegram group management bot.

## Planned features
- Group moderation: warn, mute, ban, kick, purge, locks, filters and notes
- Anti-spam, anti-raid and CAPTCHA verification
- Welcome and goodbye messages
- Group rules, admin roles and audit logs
- Analytics and optional AI-assisted moderation
- Web dashboard

## Planned stack
- Python 3.12, aiogram 3 and FastAPI
- SQLAlchemy async
- SQLite for local development; PostgreSQL for production

## Setup
Copy `.env.example` to `.env` and configure your bot token and owner settings. Never commit secrets.

GitHub Actions is used for CI and tests; it is not guaranteed 24/7 hosting.
