"""Общие инструменты для работы с бд"""

from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from sqlalchemy import insert, select
from app.db.database import async_session_maker
from app.api.models.user import UserSchema
from app.api.models.tasks import TaskSchema


class BaseDAO:
    """Общие инструменты для работы с бд. Используется как родительский класс"""

    model = None

    @classmethod
    async def find_all(cls) -> list[UserSchema | TaskSchema]:
        """Возвращает все объекты из бд"""
        async with async_session_maker() as session:
            query = select(cls.model)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_by_filter(cls, **filter_by) -> list[UserSchema | TaskSchema]:
        """Возвращает объект из бд по фильтрам"""
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def find_one_or_none(
        cls, **filter_by
    ) -> list[UserSchema | TaskSchema] | None:
        """Возвращает объект из бд по фильтрам или не возвращает ничего"""
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def add(cls, **data) -> None:
        """Добавляет объект в бд"""
        try:
            async with async_session_maker() as session:
                query = insert(cls.model).values(**data)
                await session.execute(query)
                await session.commit()
        except IntegrityError:
            raise HTTPException(status_code=409, detail="Пользователь существует")

    @classmethod
    async def delete(cls, **filter_by) -> None:
        """
        Удаляет данные по фильтрам.
        Можно удалить лишнее, поэтому указывать только уникальные данные(id, email(для пользователей), name(для тасков))
        """
        async with async_session_maker() as session:
            data = None
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            data = result.scalar_one_or_none()

            if data is None:
                raise HTTPException(
                    status_code=404, detail="Данные по таким фильтрам не найдены"
                )

            await session.delete(data)
            await session.commit()
