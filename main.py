"""Запуск приложения"""

from fastapi import FastAPI
from app.api.endpoints.users import users_router
from app.api.endpoints.tasks import tasks_router
import uvicorn

app = FastAPI(title="TO-DO List")

app.include_router(users_router)
app.include_router(tasks_router)


if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
