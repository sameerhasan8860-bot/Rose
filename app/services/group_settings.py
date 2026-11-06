from sqlalchemy import select
from app.database import SessionLocal
from app.models import Group, GroupSettings

async def get_settings(chat_id: int) -> GroupSettings:
    async with SessionLocal() as session:
        group = await session.scalar(select(Group).where(Group.telegram_id == chat_id))
        if group is None:
            group = Group(telegram_id=chat_id, title="")
            session.add(group)
            await session.flush()
        settings = await session.scalar(
            select(GroupSettings).where(GroupSettings.group_id == group.id)
        )
        if settings is None:
            settings = GroupSettings(group_id=group.id)
            session.add(settings)
        await session.commit()
        await session.refresh(settings)
        return settings

async def update_setting(chat_id: int, field: str, value):
    if field not in {"welcome_text", "anti_spam", "captcha", "anti_raid", "rules"}:
        raise ValueError("Unsupported group setting")
    async with SessionLocal() as session:
        group = await session.scalar(select(Group).where(Group.telegram_id == chat_id))
        if group is None:
            group = Group(telegram_id=chat_id, title="")
            session.add(group)
            await session.flush()
        settings = await session.scalar(
            select(GroupSettings).where(GroupSettings.group_id == group.id)
        )
        if settings is None:
            settings = GroupSettings(group_id=group.id)
            session.add(settings)
        setattr(settings, field, value)
        await session.commit()
