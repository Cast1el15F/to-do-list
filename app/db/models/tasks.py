"""Модели даных о задачах для бд"""

from sqlalchemy import Integer, String, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base
from enum import Enum
from sqlalchemy import Enum as s_Enum


class Status(str, Enum):
    new = "новая"
    in_progress = "в процессе"
    completed = "завершена"


class Tasks(Base):
    """Модель данных  пользователях для бд"""

    __tablename__ = "tasks"

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(
        default=Status.new, server_default=text("'new'"), nullable=False
    )
    status: Mapped[Status] = mapped_column(s_Enum(Status), nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
