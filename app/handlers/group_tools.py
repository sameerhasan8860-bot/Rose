import asyncio
import secrets
import time
from html import escape
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    Message, ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)
from app.services.permissions import is_group_admin
from app.services.group_settings import get_settings, update_setting
from app.services.anti_raid import register_join

router = Router()
_pending_captchas = {}
_CAPTCHA_TTL = 180


def allowed_member_permissions():
    return ChatPermissions(
        can_send_messages=True, can_send_audios=True, can_send_documents=True,
        can_send_photos=True, can_send_videos=True, can_send_video_notes=True,
        can_send_voice_notes=True, can_send_polls=True, can_send_other_messages=True,
        can_add_web_page_previews=True
    )


async def settings_keyboard(chat_id: int) -> InlineKeyboardMarkup:
    current = await get_settings(chat_id)
    captcha = "🟢 ON" if current.captcha else "⚪ OFF"
    antispam = "🟢 ON" if current.anti_spam else "⚪ OFF"
    antiraid = "🟢 ON" if current.anti_raid else "⚪ OFF"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"CAPTCHA: {captcha}", callback_data=f"mxset:{chat_id}:captcha")],
        [InlineKeyboardButton(text=f"Anti-spam: {antispam}", callback_data=f"mxset:{chat_id}:anti_spam")],
        [InlineKeyboardButton(text=f"Anti-raid: {antiraid}", callback_data=f"mxset:{chat_id}:anti_raid")],
        [InlineKeyboardButton(text="📝 Welcome message", callback_data=f"mxset:{chat_id}:welcome")],
        [InlineKeyboardButton(text="📜 Group rules", callback_data=f"mxset:{chat_id}:rules")],
        [InlineKeyboardButton(text="🔄 Refresh", callback_data=f"mxset:{chat_id}:refresh")],
    ])


async def issue_math_captcha(message: Message, member):
    left = secrets.randbelow(8) + 2
    right = secrets.randbelow(8) + 2
    answer = left + right
    choices = {answer}
    while len(choices) < 4:
        candidate = answer + secrets.choice([-4, -3, -2, -1, 1, 2, 3, 4])
        if candidate > 0:
            choices.add(candidate)
    ordered = list(choices)
    secrets.SystemRandom().shuffle(ordered)
    expires_at = time.monotonic() + _CAPTCHA_TTL
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=str(option),
            callback_data=f"mxc:{message.chat.id}:{member.id}:{option}"
        ) for option in ordered]
    ])
    sent = await message.answer(
        f"🔐 <b>Verification required</b>\n"
        f"{escape(member.full_name)}, solve this to chat:\n"
        f"<b>{left} + {right} = ?</b>\n"
        f"You have 3 minutes. Only your account can answer.",
        reply_markup=keyboard, parse_mode="HTML"
    )
    _pending_captchas[(message.chat.id, member.id)] = (answer, expires_at, sent.message_id)
    asyncio.create_task(_expire_captcha_later(
        message.bot, message.chat.id, member.id, expires_at, sent.message_id
    ))


def _pop_expired_captcha(chat_id: int, user_id: int, now=None) -> bool:
    pending = _pending_captchas.get((chat_id, user_id))
    if pending and pending[1] <= (time.monotonic() if now is None else now):
        _pending_captchas.pop((chat_id, user_id), None)
        return True
    return False


async def _expire_captcha_later(bot, chat_id: int, user_id: int, expires_at: float, message_id: int):
    await asyncio.sleep(max(0, expires_at - time.monotonic()))
    pending = _pending_captchas.get((chat_id, user_id))
    if pending and pending[1] == expires_at and _pop_expired_captcha(chat_id, user_id):
        try:
            await bot.edit_message_text(
                chat_id=chat_id, message_id=message_id,
                text="⌛ Verification expired. A group admin can use /captcharelease to review this member."
            )
        except Exception:
            pass


@router.message(Command("settings"))
async def open_settings(message: Message):
    if message.chat.type not in ("group", "supergroup") or not message.from_user:
        await message.reply("Use /settings inside the group you want to manage.")
        return
    if not await is_group_admin(message.bot, message.chat.id, message.from_user.id):
        await message.reply("Only this group's admins can open its settings.")
        return
    await message.answer(
        "⚙️ <b>MASTER X · Group settings</b>\nChoose a setting below.",
        reply_markup=await settings_keyboard(message.chat.id), parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("mxset:"))
async def change_group_setting(callback: CallbackQuery):
    try:
        _, raw_chat_id, action = (callback.data or "").split(":", 2)
        chat_id = int(raw_chat_id)
    except (ValueError, AttributeError):
        await callback.answer("Invalid settings action.", show_alert=True)
        return
    if not callback.message or callback.message.chat.id != chat_id:
        await callback.answer("Invalid panel context.", show_alert=True)
        return
    if callback.message.chat.type not in ("group", "supergroup"):
        await callback.answer("Group settings only work in groups.", show_alert=True)
        return
    if not await is_group_admin(callback.bot, chat_id, callback.from_user.id):
        await callback.answer("Only this group's admins can change settings.", show_alert=True)
        return

    current = await get_settings(chat_id)
    if action in ("captcha", "anti_spam", "anti_raid"):
        await update_setting(chat_id, action, not bool(getattr(current, action)))
        await callback.answer("Setting updated.")
    elif action in ("welcome", "rules"):
        value = current.welcome_text if action == "welcome" else current.rules
        label = "Welcome message" if action == "welcome" else "Group rules"
        command = "/setwelcome [text]" if action == "welcome" else "/setrules [text]"
        await callback.answer()
        await callback.message.answer(
            f"📝 <b>{label}</b>\n{escape(value)}\n\nChange it with {command}.", parse_mode="HTML"
        )
    elif action == "refresh":
        await callback.answer("Settings refreshed.")
    else:
        await callback.answer("Unknown setting.", show_alert=True)
        return
    await callback.message.edit_reply_markup(reply_markup=await settings_keyboard(chat_id))


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


@router.message(Command("setrules"))
async def set_rules(message: Message):
    if not message.from_user or message.chat.type not in ("group", "supergroup"):
        await message.reply("Use this command inside a group.")
        return
    if not await is_group_admin(message.bot, message.chat.id, message.from_user.id):
        await message.reply("Only group admins can change group rules.")
        return
    value = (message.text or "").partition(" ")[2].strip()
    if not value:
        await message.reply("Usage: /setrules Be respectful. No spam.")
        return
    await update_setting(message.chat.id, "rules", value[:3000])
    await message.reply("Group rules saved.")


async def toggle_setting_command(message: Message, field: str, label: str):
    if not message.from_user or message.chat.type not in ("group", "supergroup"):
        await message.reply("Use this command inside a group.")
        return
    if not await is_group_admin(message.bot, message.chat.id, message.from_user.id):
        await message.reply("Only group admins can change this setting.")
        return
    arg = (message.text or "").partition(" ")[2].strip().lower()
    if arg not in {"on", "off"}:
        current = await get_settings(message.chat.id)
        await message.reply(f"{label} is {'ON' if getattr(current, field) else 'OFF'}. Use /{field.replace('_', '')} on or off.")
        return
    await update_setting(message.chat.id, field, arg == "on")
    await message.reply(f"{label} is now {arg.upper()}.")


@router.message(Command("captcha"))
async def captcha_toggle(message: Message):
    await toggle_setting_command(message, "captcha", "CAPTCHA")


@router.message(Command("antispam"))
async def antispam_toggle(message: Message):
    await toggle_setting_command(message, "anti_spam", "Anti-spam")


@router.message(Command("antiraid"))
async def antiraid_toggle(message: Message):
    await toggle_setting_command(message, "anti_raid", "Anti-raid")


@router.message(Command("captcharelease"))
async def release_expired_captcha(message: Message):
    if not message.from_user or message.chat.type not in ("group", "supergroup"):
        await message.reply("Use this command inside the group.")
        return
    if not await is_group_admin(message.bot, message.chat.id, message.from_user.id):
        await message.reply("Only this group's admins can release a member.")
        return
    raw_user_id = (message.text or "").partition(" ")[2].strip()
    try:
        user_id = int(raw_user_id)
    except ValueError:
        await message.reply("Usage: /captcharelease USER_ID")
        return

    pending = _pending_captchas.get((message.chat.id, user_id))
    if not pending:
        await message.reply("No pending CAPTCHA was found for that user in this group.")
        return
    if _pop_expired_captcha(message.chat.id, user_id):
        await message.reply("That CAPTCHA has expired. The member is still restricted; issue a fresh verification or review them manually.")
        return
    try:
        await message.bot.restrict_chat_member(
            message.chat.id, user_id, permissions=allowed_member_permissions()
        )
        _pending_captchas.pop((message.chat.id, user_id), None)
        await message.reply(f"✅ CAPTCHA restriction released for user ID {user_id}.")
    except Exception:
        await message.reply("I couldn't release this member. Check that I have the Restrict Members admin permission.")


@router.message(F.new_chat_members)
async def welcome_new_members(message: Message):
    current = await get_settings(message.chat.id)
    for member in message.new_chat_members:
        if member.is_bot:
            continue
        raid_detected = current.anti_raid and register_join(message.chat.id)
        if current.captcha or raid_detected:
            try:
                await message.bot.restrict_chat_member(
                    message.chat.id, member.id,
                    permissions=ChatPermissions(can_send_messages=False)
                )
                await issue_math_captcha(message, member)
            except Exception:
                await message.answer(
                    f"Verification is enabled for {escape(member.full_name)}, but I need administrator permission to restrict new members."
                )
        else:
            welcome = current.welcome_text.replace("{name}", member.full_name).replace(
                "{username}", f"@{member.username}" if member.username else member.full_name
            )
            await message.answer(escape(welcome), parse_mode="HTML")


@router.callback_query(F.data.startswith("mxc:"))
async def verify_math_captcha(callback: CallbackQuery):
    try:
        _, raw_chat_id, raw_user_id, raw_choice = (callback.data or "").split(":")
        chat_id, user_id, choice = int(raw_chat_id), int(raw_user_id), int(raw_choice)
    except (ValueError, AttributeError):
        await callback.answer("Invalid verification button.", show_alert=True)
        return
    if not callback.message or callback.message.chat.id != chat_id:
        await callback.answer("Invalid verification context.", show_alert=True)
        return
    if callback.from_user.id != user_id:
        await callback.answer("This challenge belongs to another member.", show_alert=True)
        return
    pending = _pending_captchas.get((chat_id, user_id))
    if not pending or _pop_expired_captcha(chat_id, user_id):
        await callback.answer("Challenge expired. Ask a group admin for help.", show_alert=True)
        return
    if choice != pending[0]:
        await callback.answer("Not quite. Try again.", show_alert=True)
        return
    try:
        await callback.bot.restrict_chat_member(
            chat_id, user_id, permissions=allowed_member_permissions()
        )
        _pending_captchas.pop((chat_id, user_id), None)
        await callback.answer("Verification successful!")
        await callback.message.edit_text("✅ Verified successfully. Welcome to the group!")
    except Exception:
        await callback.answer("Verification failed. Please contact a group admin.", show_alert=True)
