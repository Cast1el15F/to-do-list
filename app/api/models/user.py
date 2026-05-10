"""Pydantic модели для пользователей"""

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserSchema(User):
    id: int
