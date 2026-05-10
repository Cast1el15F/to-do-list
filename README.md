# To-Do List API

Это REST API для управления списком задач (To-Do List), построенное на FastAPI. Приложение позволяет пользователям регистрироваться, авторизовываться и управлять своими задачами.

## Функциональность

- **Пользователи**:
  - Регистрация нового пользователя
  - Авторизация (логин)
  - Выход из системы (логаут)

- **Задачи**:
  - Создание новой задачи
  - Получение списка всех задач пользователя
  - Получение конкретной задачи
  - Обновление задачи
  - Удаление задачи

## Технологии

- **FastAPI** - веб-фреймворк для создания API
- **SQLAlchemy** - ORM для работы с базой данных
- **Alembic** - миграции базы данных
- **aiosqlite** - асинхронная база данных SQLite
- **Pydantic** - валидация данных
- **python-jose** - работа с JWT токенами
- **bcrypt** - хеширование паролей
- **pytest** - тестирование
- **httpx** - HTTP клиент для тестов

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone <repository-url>
   cd to-do-list
   ```

2. Создайте виртуальное окружение:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # На Windows: .venv\Scripts\activate
   ```

3. Установите зависимости:
   ```bash
   pip install -e .
   ```

4. Создайте файл `.env` в корне проекта со следующими переменными:
   ```
   MODE=dev
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   DATABASE_PATH=sqlite+aiosqlite:///./database.db
   TEST_DATABASE_PATH=sqlite+aiosqlite:///./test_database.db
   ```

5. Запустите миграции базы данных:
   ```bash
   alembic upgrade head
   ```

## Запуск

Запустите приложение с помощью uvicorn:
```bash
uvicorn main:app --reload
```

Приложение будет доступно по адресу: http://127.0.0.1:8000

Документация API доступна по адресу: http://127.0.0.1:8000/docs

## API Endpoints

### Пользователи

- `POST /user/register` - Регистрация нового пользователя
- `POST /user/login` - Авторизация пользователя
- `POST /user/logout` - Выход из системы

### Задачи

- `GET /task/my_tasks` - Получить все задачи пользователя
- `POST /task/add` - Создать новую задачу
- `PATCH /task/update` - Обновить задачу (по имени или ID)
- `DELETE /task/delete` - Удалить задачу (по ID или имени)

### Дополнительные

- `GET /all_users` - Получить всех пользователей (для отладки)
- `GET /all_tasks` - Получить все задачи (для отладки)

## Структура проекта

```
to-do-list/
├── alembic/                 # Миграции базы данных
├── app/
│   ├── api/
│   │   └── endpoints/       # API endpoints
│   │       ├── tasks.py
│   │       └── users.py
│   ├── core/
│   │   ├── config.py        # Конфигурация
│   │   └── security.py      # Безопасность (JWT)
│   └── db/
│       ├── dao/             # Data Access Objects
│       ├── models/          # SQLAlchemy модели
│       └── database.py      # Настройки базы данных
├── tests/
│   └── unit_tests/          # Тесты
├── main.py                  # Точка входа приложения
├── pyproject.toml           # Зависимости и настройки проекта
└── README.md
```

## Тестирование

Запустите тесты с помощью pytest:
```bash
pytest
```

Для запуска конкретного теста:
```bash
pytest tests/unit_tests/test_endpoints.py::test_logout_clears_cookie
```