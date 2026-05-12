"""Управление таблицей users"""

from fastapi import HTTPException
from sqlalchemy import select

from app.schemas.user import UserSchema
from app.db.dao.base_dao import BaseDAO
from app.db.models.users import Users
from app.db.database import async_session_maker


class UsersDAO(BaseDAO):
    """Управляет данными из таблицы users"""

    model = Users

    @classmethod
    async def update(
        cls,
        from_user: UserSchema | None = None,
        id: int | None = None,
        name: str | None = None,
        email: str | None = None,
        password: str | None = None,
        admin: bool | None = None,
    ) -> UserSchema:
        """Обновляет пользователя по id или по email"""
        if id is None and email is None:
            return None

        async with async_session_maker() as session:
            user = None
            if id is not None:
                user = await session.get(cls.model, id)

            if user is None and email is not None:
                user = await cls.find_one_or_none(email=email)

            if user is None:
                return None

            # Меняем только те поля, которые переданы.
            if name is not None:
                user.name = name
            if email is not None:
                user.email = email
            if password is not None:
                user.password = password
            if admin is not None:
                if from_user.admin == True:
                    user.admin = admin
                else:
                    raise HTTPException(status_code=403, detail="Недостаточно прав")

            if from_user.id != user.id and not from_user.admin:
                raise HTTPException(status_code=403, detail="Недостаточно прав")

            await session.commit()
            await session.refresh(user)
            return user
