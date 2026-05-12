"""Управление таблицей tasks"""

from fastapi import HTTPException
from sqlalchemy import select

from app.schemas.tasks import TaskSchema
from app.db.dao.base_dao import BaseDAO
from app.db.models.tasks import Tasks
from app.db.database import async_session_maker


class TasksDAO(BaseDAO):
    """Управляет данными из таблицы tasks"""

    model = Tasks

    @classmethod
    async def update(
        cls,
        user_id: int,
        id: int | None = None,
        name: str | None = None,
        description: str | None = None,
        status: str | None = None,
    ) -> TaskSchema:
        """Обновляет задачу по id"""
        if id is None:
            return None

        async with async_session_maker() as session:
            task = None
            if id is not None:
                task = await session.get(cls.model, id)

            if task.user_id != user_id:
                raise HTTPException(status_code=404, detail="У вас нет такой задачи")

            if task is None:
                return None

            # Меняем только те поля, которые переданы.
            if name is not None:
                task.name = name
            if description is not None:
                task.description = description
            if status is not None:
                task.status = status

            await session.commit()
            await session.refresh(task)
            return task
