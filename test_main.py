from fastapi.testclient import TestClient
from main import app

# Создаем клиент для тестирования
client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200

def test_get_users():
    # Регистрация нового пользователя с уникальными данными
    client.post(
        "/register/",
        json={"username": "testuser_unique1", "email": "testuser_unique1@example.com", "full_name": "Test User Unique 1", "password": "password123"},
    )

    # Получаем токен
    response = client.post(
        "/token",
        data={"username": "testuser_unique1", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    token = data["access_token"]

    response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["username"] == "testuser_unique1"

    
# Задание 1: Тестирование регистрации пользователя
def test_create_user():
    response = client.post(
        "/register/",
        json={"username": "testuser_unique2", "email": "testuser_unique2@example.com", "full_name": "Test User Unique 2", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser_unique2"
    assert data["email"] == "testuser_unique2@example.com"

    # Проверка повторной регистрации с тем же username или email
    response = client.post(
        "/register/",
        json={"username": "testuser_unique2", "email": "testuser_unique2@example.com", "full_name": "Test User Unique 2", "password": "password123"},
    )
    assert response.status_code == 400


# Задание 2: Тестирование аутентификации
def test_login_for_access_token():
    # Регистрация нового пользователя
    client.post(
        "/register/",
        json={"username": "testuser3", "email": "testuser3@example.com", "full_name": "Test User 3", "password": "password123"},
    )

    response = client.post(
        "/token",
        data={"username": "testuser3", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Проверка неправильного username или password
    response = client.post(
        "/token",
        data={"username": "testuser3", "password": "wrongpassword"},
    )
    assert response.status_code == 401

    # Проверка истекшего или неправильного токена
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalidtoken"},
    )
    assert response.status_code == 401

# Задание 3: Тестирование получения пользователей
def test_get_users_list():
    # Регистрация нового пользователя с уникальными данными
    client.post(
        "/register/",
        json={"username": "testuser_unique4", "email": "testuser_unique4@example.com", "full_name": "Test User Unique 4", "password": "password123"},
    )

    # Получаем токен
    response = client.post(
        "/token",
        data={"username": "testuser_unique4", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    token = data["access_token"]

    response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["username"] == "testuser_unique4"
    assert data[0]["email"] == "testuser_unique4@example.com"

def test_get_current_user():
    # Регистрация нового пользователя
    client.post(
        "/register/",
        json={"username": "testuser5", "email": "testuser5@example.com", "full_name": "Test User 5", "password": "password123"},
    )

    # Сначала получим токен
    response = client.post(
        "/token",
        data={"username": "testuser5", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    token = data["access_token"]

    # Получаем информацию о текущем пользователе
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser5"

# Задание 4: Тестирование обновления пользователя
def test_update_user():
    # Регистрация нового пользователя с уникальными данными
    response = client.post(
        "/register/",
        json={"username": "testuser_unique6", "email": "testuser_unique6@example.com", "full_name": "Test User Unique 6", "password": "password123"},
    )
    assert response.status_code == 200
    user_id = response.json()["id"]

    # Сначала получим токен
    response = client.post(
        "/token",
        data={"username": "testuser_unique6", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    token = data["access_token"]

    # Обновляем данные пользователя
    response = client.put(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "Updated Test User Unique 6"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Test User Unique 6"

    # Проверка обновления с некорректными данными
    response = client.put(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "invalidemail"},
    )
    assert response.status_code == 400

    # Проверка обновления без правильного токена
    response = client.put(
        f"/users/{user_id}",
        headers={"Authorization": "Bearer invalidtoken"},
        json={"full_name": "Updated Test User Unique 6"},
    )
    assert response.status_code == 401

# Задание 5: Тестирование удаления пользователя
def test_delete_user():
    # Регистрация нового пользователя
    response = client.post(
        "/register/",
        json={"username": "testuser7", "email": "testuser7@example.com", "full_name": "Test User 7", "password": "password123"},
    )
    assert response.status_code == 200
    user_id = response.json()["id"]

    # Сначала получим токен
    response = client.post(
        "/token",
        data={"username": "testuser7", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    token = data["access_token"]

    # Удаляем пользователя
    response = client.delete(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    # Повторная попытка удалить того же пользователя
    response = client.delete(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404

# Задание 6: Тестирование работы CORS
def test_cors():
    response = client.get("/")
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "*"


# Задание 7: Тестирование обработки ошибок
def test_error_handling():
    # Запрос с некорректными данными (отсутствует обязательное поле)
    response = client.post(
        "/register/",
        json={"username": "", "email": "testuser8@example.com", "full_name": "Test User 8", "password": "password123"},
    )
    assert response.status_code == 400

# Задание 8: Тестирование производительности
def test_performance():
    import time
    start_time = time.time()
    for _ in range(100):
        response = client.get("/")
        assert response.status_code == 200
    end_time = time.time()
    assert end_time - start_time < 5  # Проверка, что время отклика менее 5 секунд для 100 запросов

# Задание 9: Тестирование безопасности
def test_security():
    # Проверка, что защищенные маршруты недоступны без токена
    response = client.get("/users/me")
    assert response.status_code == 401

    # Проверка, что защищенные маршруты недоступны с неверным токеном
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalidtoken"},
    )
    assert response.status_code == 401
