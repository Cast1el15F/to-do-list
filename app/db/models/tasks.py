"""Модели даных о задачах для бд"""

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


class Tasks(Base):
    """Модель данных  пользователях для бд"""

    __tablename__ = "tasks"

    description: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
