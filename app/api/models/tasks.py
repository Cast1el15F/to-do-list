"""Pydantic модели для задач"""

from enum import Enum
from pydantic import BaseModel


class Status(str, Enum):
    new = "новая"
    in_progress = "в процессе"
    completed = "завершена"


class Task(BaseModel):
    """Модель данных о задаче"""

    name: str
    description: str
    status: Status = Status.new
    # user_id: int


class TaskSchema(Task):
    id: int
