"""Тесты"""

import uuid
from httpx import AsyncClient


def _unique_email() -> str:
    """Генерирует уникальный email"""
    return f"user_{uuid.uuid4().hex[:8]}@example.com"


def _unique_task_name() -> str:
    """Генерирует уникальное имя"""
    return f"task_{uuid.uuid4().hex[:8]}"


async def _register_user(ac: AsyncClient, name: str, email: str, password: str):
    """Регестрируем пользователя"""
    return await ac.post(
        "/user/register",
        json={
            "name": name,
            "email": email,
            "password": password,
        },
    )


async def _login_user(ac: AsyncClient, name: str, email: str, password: str):
    """Логиним пользователя"""
    return await ac.post(
        "/user/login",
        json={
            "name": name,
            "email": email,
            "password": password,
        },
    )


async def _add_task(
    ac: AsyncClient, name: str, description: str, status: str = "новая"
):
    """Добавляем пользователя"""
    return await ac.post(
        "/task/add",
        json={
            "name": name,
            "description": description,
            "status": status,
        },
    )


async def test_register_and_login_user(ac: AsyncClient):
    """Запуск тестов на регистацию и вход"""
    email = _unique_email()
    password = "complex_password_123"
    name = "TestUser"

    response = await _register_user(ac, name, email, password)
    assert response.status_code == 200

    duplicate = await _register_user(ac, name, email, password)
    assert duplicate.status_code == 409

    invalid = await _register_user(ac, name, "invalid-email", password)
    assert invalid.status_code == 422

    response = await _login_user(ac, name, email, password)
    assert response.status_code == 200
    assert "jwt_token" in response.cookies


async def test_login_user_bad_credentials_returns_401(ac: AsyncClient):
    """Тест входа с неправильным паролем"""
    email = _unique_email()
    password = "password_1"
    name = "UserBadAuth"

    response = await _register_user(ac, name, email, password)
    assert response.status_code == 200

    wrong_password = await _login_user(ac, name, email, "wrong_password")
    assert wrong_password.status_code == 401


async def test_logout_clears_cookie(ac: AsyncClient):
    """Запускает тест выхода из аккаунта"""
    email = _unique_email()
    password = "password_logout"
    name = "LogoutUser"

    response = await _register_user(ac, name, email, password)
    assert response.status_code == 200

    login_response = await _login_user(ac, name, email, password)
    assert login_response.status_code == 200
    assert "jwt_token" in login_response.cookies

    logout_response = await ac.post("/user/logout")
    assert logout_response.status_code == 200
    assert "jwt_token" in "\n".join(logout_response.headers.get_list("set-cookie"))


async def test_all_users_includes_registered_user(ac: AsyncClient):
    """
    1. Регистрирует пользователя
    2. Получает список всех пользователей
    3. Убеждаемся что новый пользователь есть в списке
    """
    email = _unique_email()
    password = "password_users"
    name = "UserListTest"

    response = await _register_user(ac, name, email, password)
    assert response.status_code == 200

    users_response = await ac.get("/all_users")
    assert users_response.status_code == 200
    users = users_response.json()
    assert any(user["email"] == email and user["name"] == name for user in users)


async def test_task_endpoints_require_auth(ac: AsyncClient):
    """
    Проверяет, что endpoints задач требуют авторизации.

    Тест убеждается, что неавторизованный пользователь
    не может:
    - получить список своих задач;
    - создать задачу;
    - обновить задачу;
    - удалить задачу.

    Все endpoints должны возвращать HTTP 401 Unauthorized.
    """
    unauthorized = await ac.get("/task/my_tasks")
    assert unauthorized.status_code == 401

    unauthorized_add = await _add_task(ac, _unique_task_name(), "desc")
    assert unauthorized_add.status_code == 401

    unauthorized_update = await ac.patch(
        "/task/update",
        json={
            "name": _unique_task_name(),
            "description": "updated",
            "status": "в процессе",
        },
    )
    assert unauthorized_update.status_code == 401

    unauthorized_delete = await ac.delete(
        "/task/delete", params={"name": _unique_task_name()}
    )
    assert unauthorized_delete.status_code == 401


async def test_task_crud_flow(ac: AsyncClient):
    """
    Проверяет полный CRUD-сценарий для задач.

    Последовательно тестирует:
    - регистрацию пользователя;
    - авторизацию пользователя;
    - создание задачи;
    - получение задачи в списке пользователя;
    - обновление задачи;
    - удаление задачи;
    - отсутствие удалённой задачи после удаления.

    Тест подтверждает корректную работу всех
    основных операций над задачами.
    """
    email = _unique_email()
    password = "password_tasks"
    name = "TaskUser"

    response = await _register_user(ac, name, email, password)
    assert response.status_code == 200

    login_response = await _login_user(ac, name, email, password)
    assert login_response.status_code == 200

    task_name = _unique_task_name()
    task_description = "Initial task description"

    add_response = await _add_task(ac, task_name, task_description)
    assert add_response.status_code == 200

    my_tasks_response = await ac.get("/task/my_tasks")
    assert my_tasks_response.status_code == 200
    tasks = my_tasks_response.json()
    assert any(
        task["name"] == task_name and task["description"] == task_description
        for task in tasks
    )

    task = next(task for task in tasks if task["name"] == task_name)
    task_id = task["id"]

    update_response = await ac.patch(
        "/task/update",
        json={
            "name": task_name,
            "description": "Updated description",
            "status": "в процессе",
        },
    )
    assert update_response.status_code == 200

    updated_tasks = (await ac.get("/task/my_tasks")).json()
    updated_task = next(task for task in updated_tasks if task["id"] == task_id)
    assert updated_task["description"] == "Updated description"
    assert updated_task["status"] == "в процессе"

    delete_response = await ac.delete("/task/delete", params={"id": task_id})
    assert delete_response.status_code == 200

    final_tasks = (await ac.get("/task/my_tasks")).json()
    assert all(task["id"] != task_id for task in final_tasks)


async def test_all_tasks_returns_added_task(ac: AsyncClient):
    """
    Проверяет, что созданная задача появляется
    в общем списке задач.

    Тест:
    - регистрирует пользователя;
    - выполняет авторизацию;
    - создаёт новую задачу;
    - получает список всех задач;
    - убеждается, что созданная задача присутствует
      в ответе API.
    """
    email = _unique_email()
    password = "password_all_tasks"
    name = "AllTasksUser"

    response = await _register_user(ac, name, email, password)
    assert response.status_code == 200

    login_response = await _login_user(ac, name, email, password)
    assert login_response.status_code == 200

    task_name = _unique_task_name()
    task_description = "All tasks description"
    add_response = await _add_task(ac, task_name, task_description)
    assert add_response.status_code == 200

    all_tasks_response = await ac.get("/all_tasks")
    assert all_tasks_response.status_code == 200
    tasks = all_tasks_response.json()
    assert any(
        task["name"] == task_name and task["description"] == task_description
        for task in tasks
    )
