"""Получаем данные из .env"""

from typing import Literal
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Читаем данные из .env"""

    mode: Literal["dev", "test", "prod"]

    secret_key: str
    algorithm: str

    database_path: str

    test_database_path: str

    class Config:
        """Указываем расположение файла .env"""

        env_file = ".env"


settings = Settings()
