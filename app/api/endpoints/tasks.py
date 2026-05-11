"""Эндпоинты для работы с задачами"""

from fastapi import APIRouter, Depends
from app.schemas.tasks import Task, TaskSchema
from app.core.security import get_user_from_token
from app.db.dao.tasks_dao import TasksDAO

tasks_router = APIRouter(prefix="/task", tags=["Tasks"])


@tasks_router.get("/my_tasks")
async def get_my_tasks(user=Depends(get_user_from_token)) -> list[TaskSchema]:
    """Получаем все задачи пользователя"""
    return await TasksDAO.find_by_filter(user_id=user.id)


@tasks_router.post("/add")
async def add_task(task: Task, user=Depends(get_user_from_token)) -> str:
    """Добавляем задачу"""
    return await TasksDAO.add(
        name=task.name,
        description=task.description,
        status=task.status,
        user_id=user.id,
    )


@tasks_router.put("/update")
async def update_task(
    task: TaskSchema, user=Depends(get_user_from_token)
) -> TaskSchema:
    """Изменяем задачу. Поиск осуществляется по имени или id задачи"""
    return await TasksDAO.update(
        id=task.id,
        user_id=user.id,
        name=task.name,
        description=task.description,
        status=task.status,
    )


@tasks_router.delete("/delete/{task_id}")
async def delete_task(task_id: int, user=Depends(get_user_from_token)) -> None:
    """Удаляем задачу"""
    return await TasksDAO.delete(id=task_id, user_id=user.id)
