from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram import F
from app.services.permissions import is_group_admin
from app.services.group_settings import get_settings, update_setting

router = Router()

@router.message(Command("setwelcome"))
async def set_welcome(message: Message):
    if not message.from_user or message.chat.type not in ("group", "supergroup"):
        await message.reply("Use this command inside a group.")
        return
    if not await is_group_admin(message.bot, message.chat.id, message.from_user.id):
        await message.reply("Only group admins can change the welcome message.")
        return
    value = (message.text or "").partition(" ")[2].strip()
    if not value:
        await message.reply("Usage: /setwelcome Welcome {name}! Please read /rules.")
        return
    await update_setting(message.chat.id, "welcome_text", value[:1000])
    await message.reply("Welcome message saved.")

@router.message(Command("captcha"))
async def captcha_toggle(message: Message):
    if not message.from_user or message.chat.type not in ("group", "supergroup"):
        await message.reply("Use this command inside a group.")
        return
    if not await is_group_admin(message.bot, message.chat.id, message.from_user.id):
        await message.reply("Only group admins can change CAPTCHA.")
        return
    arg = (message.text or "").partition(" ")[2].strip().lower()
    if arg not in {"on", "off"}:
        current = await get_settings(message.chat.id)
        await message.reply(f"CAPTCHA is {'ON' if current.captcha else 'OFF'}. Use /captcha on or /captcha off.")
        return
    await update_setting(message.chat.id, "captcha", arg == "on")
    await message.reply(f"CAPTCHA is now {arg.upper()}.")

@router.message(Command("antispam"))
async def antispam_toggle(message: Message):
    if not message.from_user or message.chat.type not in ("group", "supergroup"):
        await message.reply("Use this command inside a group.")
        return
    if not await is_group_admin(message.bot, message.chat.id, message.from_user.id):
        await message.reply("Only group admins can change anti-spam.")
        return
    arg = (message.text or "").partition(" ")[2].strip().lower()
    if arg not in {"on", "off"}:
        current = await get_settings(message.chat.id)
        await message.reply(f"Anti-spam is {'ON' if current.anti_spam else 'OFF'}. Use /antispam on or /antispam off.")
        return
    await update_setting(message.chat.id, "anti_spam", arg == "on")
    await message.reply(f"Anti-spam is now {arg.upper()}.")

@router.message(F.new_chat_members)
async def welcome_new_members(message: Message):
    settings = await get_settings(message.chat.id)
    for member in message.new_chat_members:
        if member.is_bot:
            continue
        if settings.captcha:
            try:
                await message.bot.restrict_chat_member(
                    message.chat.id, member.id,
                    permissions=ChatPermissions(can_send_messages=False)
                )
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(
                        text="I'm human — verify",
                        callback_data=f"mxverify:{message.chat.id}:{member.id}"
                    )
                ]])
                await message.answer(
                    f"Welcome {member.full_name}! Please verify to start chatting.",
                    reply_markup=keyboard
                )
            except Exception:
                await message.answer(
                    f"Welcome {member.full_name}! CAPTCHA is enabled, but I need administrator permission to restrict new members."
                )
        else:
            welcome = settings.welcome_text.replace("{name}", member.full_name).replace("{username}", f"@{member.username}" if member.username else member.full_name)
            await message.answer(welcome)

@router.callback_query(F.data.startswith("mxverify:"))
async def verify_member(callback: CallbackQuery):
    try:
        _, chat_id, user_id = (callback.data or "").split(":")
        chat_id, user_id = int(chat_id), int(user_id)
    except (ValueError, AttributeError):
        await callback.answer("Invalid verification button.", show_alert=True)
        return
    if not callback.from_user or callback.from_user.id != user_id:
        await callback.answer("This verification button belongs to another member.", show_alert=True)
        return
    try:
        await callback.bot.restrict_chat_member(
            chat_id, user_id,
            permissions=ChatPermissions(
                can_send_messages=True, can_send_audios=True, can_send_documents=True,
                can_send_photos=True, can_send_videos=True, can_send_video_notes=True,
                can_send_voice_notes=True, can_send_polls=True, can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        await callback.answer("Verification complete!")
        if callback.message:
            await callback.message.edit_text("Verified successfully. Welcome to the group!")
    except Exception:
        await callback.answer("Verification failed. Please contact a group admin.", show_alert=True)
