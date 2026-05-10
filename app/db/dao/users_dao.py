"""Управление таблицей users"""

from sqlalchemy import select

from app.db.dao.base_dao import BaseDAO
from app.db.models.users import Users
from app.db.database import async_session_maker


class UsersDAO(BaseDAO):
    """Управляет данными из таблицы users"""

    model = Users

    @classmethod
    async def update(
        cls,
        id: int | None = None,
        name: str | None = None,
        email: str | None = None,
        password: str | None = None,
    ) -> None:
        """Обновляет пользователя по id или по email"""
        if id is None and email is None:
            return None

        async with async_session_maker() as session:
            user = None
            if id is not None:
                user = await session.get(cls.model, id)

            if user is None and email is not None:
                query = select(cls.model).filter_by(email=email)
                result = await session.execute(query)
                user = result.scalar_one_or_none()

            if user is None:
                return None

            # Меняем только те поля, которые переданы.
            if name is not None:
                user.name = name
            if password is not None:
                user.password = password

            await session.commit()
            await session.refresh(user)
