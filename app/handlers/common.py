from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(Command("start"))
async def start(message: Message):
    await message.answer("MASTER X is online. Use /help to see commands.")

@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "MASTER X — Group Management\n\n"
        "General:\n/start - bot status\n/help - command list\n/id - show IDs\n/rules - basic rules\n\n"
        "Moderation (reply to a member):\n"
        "/warn [reason] - record warning\n/mute - mute member\n/unmute - unmute member\n"
        "/ban - ban member\n/unban - remove ban\n\n"
        "Group admin settings:\n"
        "/setwelcome <text> - set welcome message; placeholders: {name}, {username}\n"
        "/captcha on|off - toggle join verification\n"
        "/antispam on|off - toggle basic flood protection\n\n"
        "Moderation requires admin rights and appropriate bot permissions."
    )

@router.message(Command("id"))
async def show_id(message: Message):
    user_id = message.from_user.id if message.from_user else "unknown"
    await message.answer(f"Chat ID: {message.chat.id}\nYour ID: {user_id}")

@router.message(Command("rules"))
async def rules(message: Message):
    await message.answer("Group rules: Be respectful. No spam. Follow the group admins.")
