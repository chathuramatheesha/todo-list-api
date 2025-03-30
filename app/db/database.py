from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncAttrs,
    async_sessionmaker,
    AsyncSession,
)

from app.config import config


# The Base class is used to define the base for all of your models.
# It's necessary to subclass this in each of your database models to enable things like queries, relationships, etc.
class Base(AsyncAttrs, DeclarativeBase):
    pass


# Creates the async engine for connecting to the database using the specified URL from config.
# 'echo' is enabled from config to log all SQL queries to the console (for debugging purposes).
engine = create_async_engine(config.DATABASE_URL, echo=config.DATABASE_ECHO)

# Session maker that is used to create instances of AsyncSession, which you can use to interact with the database asynchronously.
AsyncSessionLocal = async_sessionmaker(
    engine,  # Use the created engine to connect to the database
    class_=AsyncSession,  # Specifies the session class as AsyncSession for async operations
    expire_on_commit=False,  # Prevents SQLAlchemy from expiring objects when the transaction is committed.
)


# Dependency that provides the database session.
# It can be used in FastAPI route handlers via Depends().
async def get_db():
    # Using async with, ensuring that the session is properly closed after use.
    async with AsyncSessionLocal() as session:
        # The session is yielded so that it can be used in your route handler.
        yield session


# Initializes the database by creating the necessary tables based on the metadata defined in your models.
# This should be run at the start of your application.
async def init_db():
    # Using engine.begin() to handle a database transaction for the schema creation.
    async with engine.begin() as conn:
        # Run sync code in the context of an async operation (e.g., creating tables).
        await conn.run_sync(Base.metadata.create_all)
    # Optionally, this part below can be uncommented to check existing tables.
    # async with engine.connect() as conn:
    #     tables = await conn.run_sync(
    #         lambda sync_conn: inspect(sync_conn).get_table_names()
    #     )
