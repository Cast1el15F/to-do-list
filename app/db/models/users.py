"""Модели даных о пользователях для бд"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


class Users(Base):
    """Модель данных  пользователях для бд"""

    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
