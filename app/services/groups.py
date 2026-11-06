from sqlalchemy import select
from app.database import SessionLocal
from app.models import Group, GroupSettings

async def register_group(chat_id: int, title: str):
    async with SessionLocal() as session:
        group = await session.scalar(select(Group).where(Group.telegram_id == chat_id))
        if group is None:
            group = Group(telegram_id=chat_id, title=title)
            session.add(group)
            await session.flush()
            session.add(GroupSettings(group_id=group.id))
        else:
            group.title = title
        await session.commit()
        return group
