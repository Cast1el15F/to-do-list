"""Запуск приложения"""

from fastapi import FastAPI
from app.api.endpoints.users import user_rourer
from app.api.endpoints.tasks import task_rourer
import uvicorn

app = FastAPI(title="TO-DO List")

app.include_router(user_rourer)
app.include_router(task_rourer)


if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)