from fastapi import FastAPI
from app.api.endpoints.users import user_rourer
from app.api.endpoints.tasks import task_rourer
from app.db.dao.users_dao import UsersDAO
from app.db.dao.tasks_dao import TasksDAO
import uvicorn

app = FastAPI(title="TO-DO List")

app.include_router(user_rourer)
app.include_router(task_rourer)


@app.get("/all_users")
async def all_users():
    return await UsersDAO.find_all()


@app.get("/all_tasks")
async def all_tasks():
    return await TasksDAO.find_all()


if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
