"""База, engine и sessionmaker"""

from sqlalchemy import Integer, NullPool
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from app.core.config import settings

if settings.mode == "test":
    DB_PATH = settings.test_database_path
    DB_URL = f"sqlite+aiosqlite:{DB_PATH}"
    DB_PARAMS = {"poolclass": NullPool}
else:
    DB_PATH = settings.database_path
    DB_URL = f"sqlite+aiosqlite:{DB_PATH}"
    DB_PARAMS = {}

engine = create_async_engine(DB_URL)

async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
