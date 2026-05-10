"""Эндпоинты для работы с задачами"""

from fastapi import APIRouter, Depends
from app.api.models.tasks import Task, TaskSchema
from app.core.security import get_user_from_token
from app.db.dao.tasks_dao import TasksDAO

task_rourer = APIRouter(prefix="/task", tags=["Task"])


@task_rourer.get("/my_tasks")
async def get_my_tasks(user=Depends(get_user_from_token)) -> list[TaskSchema]:
    """Получаем все задачи пользователя"""
    return await TasksDAO.find_by_filter(user_id=user.id)


@task_rourer.post("/add")
async def add_task(task: Task, user=Depends(get_user_from_token)) -> None:
    """Добавляем задачу"""
    return await TasksDAO.add(
        name=task.name,
        description=task.description,
        status=task.status,
        user_id=user.id,
    )


@task_rourer.patch("/update")
async def update_task(task: Task, user=Depends(get_user_from_token)) -> None:
    """Изменяем задачу. Поиск осуществляется по имени или id задачи"""
    return await TasksDAO.update(
        user_id=user.id,
        name=task.name,
        description=task.description,
        status=task.status,
    )


@task_rourer.delete("/delete")
async def delete_task(
    id: int | None = None, name: str | None = None, user=Depends(get_user_from_token)
) -> None:
    """Удаляем задачу"""
    if id:
        return await TasksDAO.delete(id=id, user_id=user.id)
    elif name:
        return await TasksDAO.delete(name=name, user_id=user.id)
