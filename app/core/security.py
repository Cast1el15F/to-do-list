"""Управление jwt токенами и паролями"""

from fastapi import Depends, HTTPException, Request
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.api.models.user import User, UserSchema
from app.core.config import settings
from app.db.dao.users_dao import UsersDAO

pwd_context = CryptContext(schemes=["pbkdf2_sha256"])


async def get_password_hash(password: str) -> str:
    """Возвращает хешированный пароль"""
    return pwd_context.hash(password)


async def verify_password(
    plain_password: str | bytes, hashed_password: str | bytes
) -> bool:
    """Сверяет полученный пароль и хешированный"""
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(user_data: User) -> User:
    """Возвращает пользователя если он есть в бд"""
    user = await UsersDAO.find_one_or_none(email=user_data.email)
    if not user:
        return None
    if not await verify_password(user_data.password, user.password):
        return None
    return user


async def create_jwt_token(data: dict) -> str:
    """Функция для создания JWT токена. Мы копируем входные данные, добавляем время истечения и кодируем токен."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, key=settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


async def get_token(request: Request) -> str:
    """Получаем токен из cookes"""
    token = request.cookies.get("jwt_token")
    if not token:
        raise HTTPException(status_code=401)
    return token


async def get_user_from_token(token: str = Depends(get_token)) -> UserSchema:
    """Функция для извлечения информации о пользователе из токена. Проверяем токен и извлекаем утверждение о пользователе."""
    try:
        payload = jwt.decode(
            token, key=settings.secret_key, algorithms=settings.algorithm
        )
    except JWTError:
        HTTPException(status_code=401, detail="Передан не jwt токен")
    expire: float = payload.get("exp")
    if expire is None or expire < datetime.utcnow().timestamp():
        raise HTTPException(
            status_code=401,
            detail="В jwt токене не указан exp либо истек срок действия токена",
        )
    email: str = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="В jwt токене не указан sub")
    user = await UsersDAO.find_one_or_none(email=email)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    return user
