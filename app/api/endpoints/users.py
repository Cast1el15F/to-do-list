"""Эндпоинты для работы с пользователями"""

from fastapi import APIRouter, Depends, HTTPException, Response
from app.schemas.user import User, UserSchema
from app.core.security import (
    authenticate_user,
    create_jwt_token,
    get_password_hash,
    get_user_from_token,
)
from app.db.dao.users_dao import UsersDAO

users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.post("/register")
async def register_user(user_data: User) -> str:
    """Регистрируем пользователя"""
    hashed_password = await get_password_hash(user_data.password)
    return await UsersDAO.add(
        name=user_data.name,
        email=user_data.email,
        password=hashed_password,
        admin=False,
    )


@users_router.post("/login")
async def login_user(response: Response, user_data: User) -> str:
    """Логиним пользователя"""
    user = await authenticate_user(user_data=user_data)
    if not user:
        raise HTTPException(status_code=401)
    access_token = await create_jwt_token({"sub": str(user_data.email)})
    response.set_cookie("jwt_token", access_token)
    return access_token


@users_router.post("/logout")
async def logout_user(response: Response) -> None:
    """Выходим из аккаунта(удаляем кеш с jwt токеном)"""
    response.delete_cookie("jwt_token")
    return "success"


@users_router.put("/update")
async def update_user(user_data: User, user=Depends(get_user_from_token)) -> UserSchema:
    return await UsersDAO.update(
        from_user=user,
        id=user.id,
        name=user_data.name,
        email=user_data.email,
        password=user_data.password,
    )


@users_router.put("/add_admin")
async def add_admin(
    id: int | None = None, email: str | None = None, user=Depends(get_user_from_token)
) -> UserSchema:
    if id is not None:
        user = await UsersDAO.find_one_or_none(id=id)
    elif email is not None:
        user = await UsersDAO.find_one_or_none(email=email)
    return await UsersDAO.update(from_user=user, id=user.id)


@users_router.get("/users")
async def get_users(user=Depends(get_user_from_token)) -> list[UserSchema]:
    """Получаем всех пользователей"""
    if user.admin:
        return await UsersDAO.find_all()
    else:
        raise HTTPException(status_code=403, detail="Недостаточно прав")


@users_router.get("/users/{id}")
async def get_users(id: int, user=Depends(get_user_from_token)) -> UserSchema:
    """Получаем всех пользователей"""
    if user.admin:
        return await UsersDAO.find_one_or_none(id=id)
    else:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
