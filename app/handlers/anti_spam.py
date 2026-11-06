import time
from collections import defaultdict, deque
from aiogram import Router, F
from aiogram.types import Message, ChatPermissions
from app.services.group_settings import get_settings
from app.services.permissions import is_group_admin

router = Router()
_recent = defaultdict(deque)
_LIMIT = 6
_WINDOW_SECONDS = 8

@router.message(F.chat.type.in_({"group", "supergroup"}))
async def basic_flood_guard(message: Message):
    if not message.from_user or message.from_user.is_bot or not message.text:
        return
    settings = await get_settings(message.chat.id)
    if not settings.anti_spam:
        return
    try:
        if await is_group_admin(message.bot, message.chat.id, message.from_user.id):
            return
    except Exception:
        return
    now = time.monotonic()
    key = (message.chat.id, message.from_user.id)
    events = _recent[key]
    while events and now - events[0] > _WINDOW_SECONDS:
        events.popleft()
    events.append(now)
    if len(events) <= _LIMIT:
        return
    events.clear()
    try:
        await message.delete()
        await message.bot.restrict_chat_member(
            message.chat.id, message.from_user.id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=int(time.time()) + 60
        )
        await message.answer(f"{message.from_user.full_name} was temporarily muted for flooding (60 seconds).")
    except Exception:
        # Do not crash message handling if the bot lacks moderation permissions.
        return
