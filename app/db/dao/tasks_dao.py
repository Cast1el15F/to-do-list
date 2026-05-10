"""Управление таблицей tasks"""

from sqlalchemy import select

from app.db.dao.base_dao import BaseDAO
from app.db.models.tasks import Status, Tasks
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
        status: Status | None = None,
    ):
        """Обновляет пользователя по id или по имени"""
        if id is None and name is None:
            return None

        async with async_session_maker() as session:
            task = None
            if id is not None:
                task = await session.get(cls.model, id)

            if task is None and name is not None:
                query = select(cls.model).filter_by(name=name, user_id=user_id)
                result = await session.execute(query)
                task = result.scalar_one_or_none()

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
