from aiogram import Bot
from aiogram.enums import ChatMemberStatus

async def is_group_admin(bot: Bot, chat_id: int, user_id: int) -> bool:
    member = await bot.get_chat_member(chat_id, user_id)
    return member.status in (ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR)

async def can_restrict(bot: Bot, chat_id: int, actor_id: int) -> bool:
    if not await is_group_admin(bot, chat_id, actor_id):
        return False
    me = await bot.get_chat_member(chat_id, (await bot.get_me()).id)
    return me.status == ChatMemberStatus.ADMINISTRATOR and bool(
        getattr(me, "can_restrict_members", False)
    )
