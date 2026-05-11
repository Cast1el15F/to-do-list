"""Получаем данные из .env"""

from typing import Literal

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Читаем данные из .env"""

    mode: Literal["dev", "test", "prod"]

    secret_key: str
    algorithm: str

    database_path: str

    test_database_path: str

    model_config = ConfigDict(env_file=".env")


settings = Settings()
