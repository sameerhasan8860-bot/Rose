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
        "/start - status\n/help - command list\n/id - show chat and user IDs\n"
        "Group admins: /setwelcome <text>, /rules"
    )

@router.message(Command("id"))
async def show_id(message: Message):
    await message.answer(f"Chat ID: {message.chat.id}\nYour ID: {message.from_user.id}")

@router.message(Command("rules"))
async def rules(message: Message):
    await message.answer("Group rules: Be respectful. No spam. Follow the group admins.")
