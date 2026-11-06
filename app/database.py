from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.config import settings

engine = create_async_engine(settings.database_url, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


def _migrate_group_settings(sync_conn):
    inspector = inspect(sync_conn)
    if "group_settings" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("group_settings")}
    if "anti_raid" not in columns:
        sync_conn.execute(
            text("ALTER TABLE group_settings ADD COLUMN anti_raid BOOLEAN NOT NULL DEFAULT FALSE")
        )


async def init_db():
    from app.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_migrate_group_settings)
