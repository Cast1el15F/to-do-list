"""Pydantic модели для пользователей"""

from enum import Enum
from pydantic import BaseModel, EmailStr


class User(BaseModel):
    name: str
    email: EmailStr
    password: str
    admin: bool = False


class UserSchema(User):
    id: int
