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
        "MASTER X commands:\n"
        "/start - bot status\n"
        "/help - this command list\n"
        "/id - show chat and user IDs\n"
        "/rules - show basic group rules\n\n"
        "Reply to a member's message to use:\n"
        "/warn [reason] - record a warning\n"
        "/mute - restrict messages\n"
        "/unmute - restore messaging\n"
        "/ban - ban member\n"
        "/unban - remove ban\n\n"
        "Moderation commands require group-admin rights and bot permissions."
    )

@router.message(Command("id"))
async def show_id(message: Message):
    user_id = message.from_user.id if message.from_user else "unknown"
    await message.answer(f"Chat ID: {message.chat.id}\nYour ID: {user_id}")

@router.message(Command("rules"))
async def rules(message: Message):
    await message.answer("Group rules: Be respectful. No spam. Follow the group admins.")
