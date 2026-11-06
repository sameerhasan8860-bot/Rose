import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import ChatMemberUpdated
from app.config import settings
from app.database import init_db
from app.handlers.common import router
from app.services.groups import register_group

async def on_chat_member(event: ChatMemberUpdated):
    chat = event.chat
    if chat.type in ("group", "supergroup"):
        await register_group(chat.id, chat.title or "")

async def main():
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is missing. Copy .env.example to .env and set it.")
    logging.basicConfig(level=settings.log_level)
    await init_db()
    bot = Bot(settings.bot_token)
    dp = Dispatcher()
    dp.include_router(router)
    dp.chat_member.register(on_chat_member)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
