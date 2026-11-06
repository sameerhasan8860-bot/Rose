from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery

router = Router()

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛡 Group settings", callback_data="mxmenu:settings")],
        [InlineKeyboardButton(text="📖 Help & commands", callback_data="mxmenu:help")],
    ])

def help_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ Open group settings", callback_data="mxmenu:settings")],
        [InlineKeyboardButton(text="⬅️ Main menu", callback_data="mxmenu:home")],
    ])

@router.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "🛡 <b>MASTER X</b>\nYour group protection and management assistant.\n\n"
        "Add me to a group and grant the permissions needed for moderation.",
        reply_markup=main_menu(), parse_mode="HTML"
    )

@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "🛡 <b>MASTER X — Commands</b>\n\n"
        "<b>General</b>\n/start — Main menu\n/help — Show commands\n"
        "/id — Show IDs\n/rules — Show group rules\n/settings — Group settings\n\n"
        "<b>Moderation</b> (reply to a member)\n"
        "/warn [reason] · /mute · /unmute · /ban · /unban\n\n"
        "<b>Group setup</b> (admins only)\n"
        "/setwelcome [text] · /setrules [text]\n"
        "/captcha on|off · /antispam on|off",
        reply_markup=help_menu(), parse_mode="HTML"
    )

@router.message(Command("id"))
async def show_id(message: Message):
    user_id = message.from_user.id if message.from_user else "unknown"
    await message.answer(f"Chat ID: {message.chat.id}\nYour ID: {user_id}")

@router.message(Command("rules"))
async def rules(message: Message):
    from app.services.group_settings import get_settings
    current = await get_settings(message.chat.id)
    await message.answer(f"📜 <b>Group rules</b>\n{current.rules}", parse_mode="HTML")

@router.callback_query(F.data.startswith("mxmenu:"))
async def menu_navigation(callback: CallbackQuery):
    action = (callback.data or "").split(":", 1)[1]
    if action == "settings":
        if not callback.message or callback.message.chat.type not in ("group", "supergroup"):
            await callback.answer("Run /settings inside the group you want to manage.", show_alert=True)
            return
        from app.handlers.group_tools import settings_keyboard
        from app.services.permissions import is_group_admin
        if not await is_group_admin(callback.bot, callback.message.chat.id, callback.from_user.id):
            await callback.answer("Only this group's admins can open its settings.", show_alert=True)
            return
        await callback.message.edit_text(
            "⚙️ <b>MASTER X · Group settings</b>\nChoose a setting below.",
            reply_markup=await settings_keyboard(callback.message.chat.id), parse_mode="HTML"
        )
    elif action == "help":
        await callback.message.edit_text(
            "📖 <b>MASTER X — Quick help</b>\n/settings — Group settings\n"
            "/setwelcome — Welcome text\n/setrules — Group rules\n"
            "/captcha on|off — Join verification\n/antispam on|off — Flood protection\n"
            "/warn · /mute · /unmute · /ban · /unban",
            reply_markup=help_menu(), parse_mode="HTML"
        )
    elif action == "home":
        await callback.message.edit_text(
            "🛡 <b>MASTER X</b>\nYour group protection and management assistant.",
            reply_markup=main_menu(), parse_mode="HTML"
        )
    await callback.answer()
