import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def registered_user():
    # Регистрация нового пользователя
    response = client.post(
        "/register/",
        json={"username": "testuser", "email": "testuser@example.com", "full_name": "Test User", "password": "password123"},
    )
    assert response.status_code == 200
    user_data = response.json()

    # Получение токена
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "password123"},
    )
    assert response.status_code == 200
    token_data = response.json()

    return user_data, token_data["access_token"]

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200

# Задание 1: Тестирование регистрации пользователя
def test_create_user(registered_user):
    user_data, token = registered_user

    # Проверка повторной регистрации с тем же username или email
    response = client.post(
        "/register/",
        json={"username": "testuser", "email": "testuser@example.com", "full_name": "Test User", "password": "password123"},
    )
    assert response.status_code == 400

# Задание 2: Тестирование аутентификации
def test_login_for_access_token(registered_user):
    user_data, token = registered_user

    # Проверка успешной аутентификации пользователя и получения токена
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Проверка неправильного username или password
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "wrongpassword"},
    )
    assert response.status_code == 401

    # Проверка истекшего или неправильного токена
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalidtoken"},
    )
    assert response.status_code == 401

# Задание 3: Тестирование получения пользователей
def test_get_users_list(registered_user):
    user_data, token = registered_user

    # Проверка успешного получения списка пользователей
    response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(user["username"] == "testuser" for user in data)

def test_get_current_user(registered_user):
    user_data, token = registered_user

    # Проверка получения информации о текущем пользователе с правильным токеном
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"

# Задание 4: Тестирование обновления пользователя
def test_update_user(registered_user):
    user_data, token = registered_user
    user_id = user_data["id"]

    # Проверка обновления данных пользователя
    response = client.put(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "Updated Test User"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Test User"

    # Проверка обновления с некорректными данными
    response = client.put(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "invalidemail"},
    )
    assert response.status_code == 422

    # Проверка обновления без правильного токена
    response = client.put(
        f"/users/{user_id}",
        headers={"Authorization": "Bearer invalidtoken"},
        json={"full_name": "Updated Test User"},
    )
    assert response.status_code == 401

# Задание 5: Тестирование удаления пользователя
def test_delete_user(registered_user):
    user_data, token = registered_user
    user_id = user_data["id"]

    # Проверка успешного удаления пользователя
    response = client.delete(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    # Проверка повторной попытки удалить того же пользователя
    response = client.delete(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404

# Задание 6: Тестирование работы CORS
def test_cors():
    # Проверка работы CORS с запросами из разрешенного источника
    response = client.get("/", headers={"Origin": "http://allowed-origin.com"})
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://allowed-origin.com"