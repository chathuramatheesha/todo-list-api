from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncAttrs,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import inspect

from app.config import config


class Base(AsyncAttrs, DeclarativeBase):
    pass


engine = create_async_engine(config.DATABASE_URL, echo=config.DATABASE_ECHO)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # async with engine.connect() as conn:
    #     tables = await conn.run_sync(
    #         lambda sync_conn: inspect(sync_conn).get_table_names()
    #     )
