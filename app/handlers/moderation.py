from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ChatPermissions
from app.database import SessionLocal
from app.models import Warning
from app.services.permissions import can_restrict

router = Router()

def target_from_reply(message: Message):
    return message.reply_to_message.from_user if message.reply_to_message else None

@router.message(Command("warn"))
async def warn_user(message: Message):
    target = target_from_reply(message)
    if not target or not message.from_user:
        await message.reply("Reply to a user's message: /warn [reason]")
        return
    if not await can_restrict(message.bot, message.chat.id, message.from_user.id):
        await message.reply("Only an admin can use this command, and the bot needs restrict-member permission.")
        return
    reason = (message.text or "").partition(" ")[2].strip() or "No reason provided"
    async with SessionLocal() as session:
        session.add(Warning(chat_id=message.chat.id, user_id=target.id,
                            admin_id=message.from_user.id, reason=reason))
        await session.commit()
    await message.reply(f"⚠️ Warning recorded for {target.full_name}. Reason: {reason}")

@router.message(Command("mute"))
async def mute_user(message: Message):
    target = target_from_reply(message)
    if not target or not message.from_user:
        await message.reply("Reply to a user's message: /mute")
        return
    if not await can_restrict(message.bot, message.chat.id, message.from_user.id):
        await message.reply("Admin permission required. The bot also needs restrict-member permission.")
        return
    await message.bot.restrict_chat_member(
        message.chat.id, target.id,
        permissions=ChatPermissions(can_send_messages=False)
    )
    await message.reply(f"Muted {target.full_name}.")

@router.message(Command("unmute"))
async def unmute_user(message: Message):
    target = target_from_reply(message)
    if not target or not message.from_user:
        await message.reply("Reply to a user's message: /unmute")
        return
    if not await can_restrict(message.bot, message.chat.id, message.from_user.id):
        await message.reply("Admin permission required. The bot also needs restrict-member permission.")
        return
    await message.bot.restrict_chat_member(
        message.chat.id, target.id,
        permissions=ChatPermissions(
            can_send_messages=True, can_send_audios=True, can_send_documents=True,
            can_send_photos=True, can_send_videos=True, can_send_video_notes=True,
            can_send_voice_notes=True, can_send_polls=True, can_send_other_messages=True,
            can_add_web_page_previews=True
        )
    )
    await message.reply(f"Unmuted {target.full_name}.")

@router.message(Command("ban"))
async def ban_user(message: Message):
    target = target_from_reply(message)
    if not target or not message.from_user:
        await message.reply("Reply to a user's message: /ban")
        return
    if not await can_restrict(message.bot, message.chat.id, message.from_user.id):
        await message.reply("Admin permission required. The bot also needs restrict-member permission.")
        return
    await message.bot.ban_chat_member(message.chat.id, target.id)
    await message.reply(f"Banned {target.full_name}.")

@router.message(Command("unban"))
async def unban_user(message: Message):
    target = target_from_reply(message)
    if not target or not message.from_user:
        await message.reply("Reply to a user's message: /unban")
        return
    if not await can_restrict(message.bot, message.chat.id, message.from_user.id):
        await message.reply("Admin permission required. The bot also needs restrict-member permission.")
        return
    await message.bot.unban_chat_member(message.chat.id, target.id, only_if_banned=True)
    await message.reply(f"Unbanned {target.full_name}.")
