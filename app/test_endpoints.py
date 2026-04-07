from fastapi import status
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def create_user(password="12345"):
    email = "test@gmail.com"
    response = client.post(
        "/users",
        json={"email": email, "password": password}
    )
    return response

def test_user_is_created(password="12345"):
    response = create_user(password=password)
    assert response.status_code == status.HTTP_201_CREATED

def test_login():
    password = "12345"
    users_response = create_user(password=password)
    assert users_response.status_code == status.HTTP_201_CREATED
    username = users_response.json()["username"]
    login_response = client.post(
        "/login",
        data={"username": username, "password": password}
    )
    assert login_response.status_code == status.HTTP_200_OK
    login_response = client.post(
        "/login",
        data={"username" : username, "password": "iawefoajwfeö1214"}
    )
    assert login_response.status_code == status.HTTP_401_UNAUTHORIZED
    
def test_authorized_user():
    password = "12345"
    users_response = create_user(password=password)
    assert users_response.status_code == status.HTTP_201_CREATED
    username = users_response.json()["username"]
    login_response = client.post(
        "/login",
        data={"username": username, "password": password}
    )
    assert login_response.status_code == status.HTTP_200_OK
    access_token = login_response.json()["token"]["access_token"]
    self_response = client.get(
        "/users/self",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert self_response.status_code == status.HTTP_200_OK
    assert username == self_response.json()["username"]
    self_response = client.get(
        "/users/self",
    )
    assert self_response.status_code == status.HTTP_401_UNAUTHORIZED
    