FROM python:3.14-slim

# Отключает создание .pyc файлов
ENV PYTHONDONTWRITEBYTECODE=1

# Логи Python сразу выводятся в консоль
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Установка Poetry
RUN pip install poetry

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock ./

# Poetry будет ставить зависимости прямо в контейнер
RUN poetry config virtualenvs.create false

# Установка зависимостей
RUN poetry install --no-interaction --no-ansi --no-root

# Копируем проект
COPY . .

# Открываем порт FastAPI
EXPOSE 8000

# Запуск приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]