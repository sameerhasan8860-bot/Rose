# MASTER X

Free, modular Telegram group management bot. This is an early development build, not yet a complete replacement for established moderation platforms.

## Implemented
- aiogram 3 polling bot: /start, /help, /id and /rules
- Reply-based moderation: /warn, /mute, /unmute, /ban and /unban
- Group-admin and bot-permission checks before moderation actions
- Inline MASTER X main menu with help navigation
- Admin-only per-group settings panel with CAPTCHA and anti-spam toggles
- Custom welcome text with {name} and {username} placeholders
- Custom group rules using /setrules
- Optional button-based join verification: /captcha on|off
- Optional basic flood protection: /antispam on|off
- Async SQLAlchemy models for groups, settings, warnings and filters
- FastAPI health endpoint at /health
- Environment-based configuration
- GitHub Actions compile and pytest workflow

## Setup
1. Create a Telegram bot with BotFather and copy its token.
2. Copy .env.example to .env.
3. Set BOT_TOKEN and GLOBAL_OWNER_ID in .env.
4. Install dependencies: pip install -r requirements.txt
5. Run the bot: python -m app.bot
6. Optional API: uvicorn app.api:app --host 0.0.0.0 --port 8000

Add the bot to your group as an administrator. It needs Delete Messages and Restrict Members permissions for the relevant protection features. Open the admin panel with /settings, or enable CAPTCHA with /captcha on and flood protection with /antispam on. Set group rules with /setrules [text]. Reply to a member's message to use moderation commands.

## Important limitations
- CAPTCHA currently uses a one-button human confirmation; it is not an advanced challenge and has no automatic timeout/cleanup yet.
- Flood protection is a basic in-memory per-process rate limit, not distributed or persistent.
- Anti-raid, link filtering, full analytics, AI moderation, dashboard, and global/group owner control are still planned.
- GitHub Actions runs CI/tests; it is not guaranteed 24/7 bot hosting.

Never commit .env or share your bot token.
