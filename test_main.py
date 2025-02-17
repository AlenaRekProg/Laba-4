# from fastapi.testclient import TestClient


# from main import app
# client = TestClient(app)


# def test_read_main():
#     response = client.get("/")
#     assert response.status_code == 200


# def test_get_users():
#     response = client.get("/users/")
#     assert response.status_code == 200
#     data = response.json()
#     assert len(data) > 0
#     assert data[0]["username"] == "string"

# def test_create_user():
#     response = client.post(
#         "/register/",
#         json={"username": "testuser", "email": "testuser@example.com", "full_name": "Test User", "password": "password123"},
#     )
#     assert response.status_code == 200
#     data = response.json()
#     assert data["username"] == "testuser"
#     assert data["email"] == "testuser@example.com"  