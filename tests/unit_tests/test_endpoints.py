"""Тесты"""

import uuid
from sqlalchemy import select
from app.models.users import Users
from httpx import AsyncClient


def _unique_email() -> str:
    """Генерирует уникальный email"""
    return f"user_{uuid.uuid4().hex[:8]}@example.com"


def _unique_task_name() -> str:
    """Генерирует уникальное имя"""
    return f"task_{uuid.uuid4().hex[:8]}"


async def _register_user(ac: AsyncClient, name: str, email: str, password: str):
    """Регистрирует пользователя"""
    return await ac.post(
        "/users/register",
        json={
            "name": name,
            "email": email,
            "password": password,
        },
    )


async def _login_user(ac: AsyncClient, name: str, email: str, password: str):
    """Логиним пользователя"""
    return await ac.post(
        "/users/login",
        json={
            "name": name,
            "email": email,
            "password": password,
        },
    )


async def _add_task(
    ac: AsyncClient, name: str, description: str, status: str = "новая"
):
    """Добавляем задачу"""
    return await ac.post(
        "/task/add",
        json={
            "name": name,
            "description": description,
            "status": status,
        },
    )


async def test_register_and_login_user(ac: AsyncClient):
    """Запуск тестов на регистрацию и вход"""
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

    logout_response = await ac.post("/users/logout")
    assert logout_response.status_code == 200
    assert "jwt_token" in "\n".join(logout_response.headers.get_list("set-cookie"))


async def test_update_user_profile_with_edge_case_values(ac: AsyncClient):
    """Обновление профиля пользователя с пустыми строками и спецсимволами"""
    email = _unique_email()
    password = "P@55w0rd!"
    name = "UpdateUser"

    response = await _register_user(ac, name, email, password)
    assert response.status_code == 200

    login_response = await _login_user(ac, name, email, password)
    assert login_response.status_code == 200

    new_email = _unique_email()
    long_name = "A" * 500 + "!@#"
    update_response = await ac.put(
        "/users/update",
        json={
            "name": long_name,
            "email": new_email,
            "password": "new_P@ssword!",
        },
    )
    assert update_response.status_code == 200
    profile = update_response.json()
    assert profile["name"] == long_name
    assert profile["email"] == new_email


async def test_update_user_profile_invalid_email_returns_422(ac: AsyncClient):
    """Если email невалидный, Pydantic возвращает 422"""
    email = _unique_email()
    password = "password_update"
    name = "InvalidEmailUser"

    response = await _register_user(ac, name, email, password)
    assert response.status_code == 200

    login_response = await _login_user(ac, name, email, password)
    assert login_response.status_code == 200

    invalid_update = await ac.put(
        "/users/update",
        json={
            "name": "SomeName",
            "email": "not-an-email",
            "password": "newpassword",
        },
    )
    assert invalid_update.status_code == 422


async def test_users_list_and_detail_require_admin(ac: AsyncClient, session):
    """Доступ к списку пользователей и пользователю по id запрещён для обычных пользователей"""
    email = _unique_email()
    password = "password_admin"
    name = "NonAdminUser"

    response = await _register_user(ac, name, email, password)
    assert response.status_code == 200

    login_response = await _login_user(ac, name, email, password)
    assert login_response.status_code == 200

    user_result = await session.execute(select(Users).filter_by(email=email))
    user = user_result.scalar_one()

    users_response = await ac.get("/users/users")
    assert users_response.status_code == 403

    detail_response = await ac.get(f"/users/users/{user.id}")
    assert detail_response.status_code == 403


async def test_admin_can_get_user_list_and_detail(ac: AsyncClient, session):
    """Администратор может получить список пользователей и профиль по id"""
    admin_email = _unique_email()
    admin_password = "admin_password"
    admin_name = "AdminUser"

    target_email = _unique_email()
    target_password = "target_password"
    target_name = "TargetUser"

    assert (
        await _register_user(ac, admin_name, admin_email, admin_password)
    ).status_code == 200
    assert (
        await _register_user(ac, target_name, target_email, target_password)
    ).status_code == 200

    result = await session.execute(select(Users).filter_by(email=admin_email))
    admin_user = result.scalar_one()
    admin_user.admin = True
    await session.commit()

    login_response = await _login_user(ac, admin_name, admin_email, admin_password)
    assert login_response.status_code == 200

    list_response = await ac.get("/users/users")
    assert list_response.status_code == 200
    users = list_response.json()
    assert any(user["email"] == target_email for user in users)

    target_result = await session.execute(select(Users).filter_by(email=target_email))
    target_user = target_result.scalar_one()

    detail_response = await ac.get(f"/users/users/{target_user.id}")
    assert detail_response.status_code == 200
    user = detail_response.json()
    assert user["email"] == target_email


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

    unauthorized_update = await ac.put(
        "/task/update",
        json={
            "id": 1,
            "name": _unique_task_name(),
            "description": "updated",
            "status": "в процессе",
        },
    )
    assert unauthorized_update.status_code == 401

    unauthorized_delete = await ac.delete("/task/delete/1")
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

    update_response = await ac.put(
        "/task/update",
        json={
            "id": task_id,
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

    delete_response = await ac.delete(f"/task/delete/{task_id}")
    assert delete_response.status_code == 200

    final_tasks = (await ac.get("/task/my_tasks")).json()
    assert all(task["id"] != task_id for task in final_tasks)


async def test_my_tasks_returns_added_task(ac: AsyncClient):
    """
    Проверяет, что созданная задача появляется
    в списке пользователя.
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

    my_tasks_response = await ac.get("/task/my_tasks")
    assert my_tasks_response.status_code == 200
    tasks = my_tasks_response.json()
    assert any(
        task["name"] == task_name and task["description"] == task_description
        for task in tasks
    )
