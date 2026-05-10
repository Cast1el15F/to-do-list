"""Настройки для тестов"""

import os
import json
from pytest import fixture
from sqlalchemy import insert
from app.db.database import Base, async_session_maker, engine
from app.core.config import settings
import asyncio
from httpx import ASGITransport, AsyncClient
from main import app as fastapi_app

from app.db.models.users import Users

os.environ["mode"] = "test"


@fixture(scope="session", autouse=True)
async def prepare_database():
    assert settings.mode == "test"

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    def open_mock_json(model: str):
        mock_files = {
            "user": "tests/mock_users.json",
            "task": "tests/mock_tasks.json",
        }
        path = mock_files.get(model, f"tests/mock_{model}.json")
        with open(path, encoding="utf-8") as file:
            return json.load(file)

    user = open_mock_json("user")
    # currency = open_mock_json("currency")

    async with async_session_maker() as session:
        add_user = insert(Users).values(user)

        await session.execute(add_user)
        await session.commit()


@fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@fixture(scope="function")
async def ac():
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@fixture(scope="function")
async def session():
    """Возвращает новую сессию"""
    async with async_session_maker() as session:
        yield session
