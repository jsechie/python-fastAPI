from app import schemas
from .database import fake,settings
from jose import jwt
import pytest

user_data = {
            "email":fake.email(domain=fake.free_email_domain()),"firstname":fake.first_name(),
            "lastname":fake.last_name(),"username":fake.user_name(),"password":"Password123"
         }

def test_api_status(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json().get('message') == "API is up and running"

def test_user_creation(client):
    response = client.post("/users", json=user_data)
    new_user = schemas.UserResponse(**response.json())
    assert response.status_code == 201
    assert user_data['email'] == new_user.email


@pytest.mark.parametrize("email, firstname, lastname, username, password",[
    (fake.email(domain=fake.free_email_domain()),fake.first_name(),fake.last_name(),fake.user_name(),None),
    (fake.email(domain=fake.free_email_domain()),fake.first_name(),fake.last_name(),None,None),
    (fake.email(domain=fake.free_email_domain()),fake.first_name(),None,None,None),
    (fake.email(domain=fake.free_email_domain()),None,None,None,None),
    (None,None,None,None,None)
])
def test_user_creation_missing_body(client, email, firstname, lastname, username, password):
    data = {"email":email,"firstname":firstname,"lastname":lastname,"username":username,"password":password}
    response = client.post("/users", json=data)
    assert response.status_code == 422

def test_user_login(client, test_user):
    response = client.post("/login", data={"username":test_user['email'],"password":test_user['password']})
    token = schemas.Token(**response.json())
    assert token.token_type == "bearer"
    assert token.expires_in == "15 minutes"
    payload = jwt.decode(token.access_token, settings.secret_key, algorithms=[settings.algorithm])
    id: str = payload.get("id")
    assert id == test_user['id']
    assert response.status_code == 200

@pytest.mark.parametrize("email, password, status_code",[
    ('wrongemail@gmail.com','Password123',403),
    ('correctemail@gmail.com','wrongPassword',403),
    ('wrongemail@gmail.com','wrongPassword',403),
    (None,'Password123',422),
    ('correctemail@gmail.com',None,422)
])
def test_incorrect_user_login(client, email, password, status_code):
    response = client.post("/login", data={"username":email,"password":password})
    assert response.status_code == status_code


def test_get_single_user(auth_client, test_user):
    response = auth_client.get(f"/users/{test_user['uuid']}")
    user = schemas.UserResponse(**response.json())
    assert user.uuid == test_user['uuid']
    assert response.status_code == 200


def test_get_single_user_id_not_exist(auth_client):
    user_id = "3e04d503-ddd2-4190-914a-bf5e10be8048"
    response = auth_client.get(f"/users/{user_id}")
    assert response.json().get('detail') == f"User with id {user_id} not found"
    assert response.status_code == 404

def test_get_single_user_invalid_token(client, test_user):
    access_token = "eyJpZCI6NSwiZXhwIjoxNjc4Njc3NzUwfQ.uyaFKOiuaFCsbG001Hh4uyzikPFGG_ubumwqKiLWUxc.eyJpZCI6NSwiZXhwIjoxNjc4Njc3NzUwfQ"
    client.headers = {**client.headers,"Authorization": f"Bearer {access_token}"}
    response = client.get(f"/users/{test_user['uuid']}")
    assert response.json().get('detail') == f"Could not validate credentials"
    assert response.status_code == 401

def test_get_single_user_unathorized(client, test_user):
    response = client.get(f"/users/{test_user['uuid']}")
    assert response.json().get('detail') == f"Not authenticated"
    assert response.status_code == 401

def test_get_all_users(auth_client):
    response = auth_client.get(f"/users")
    user = response.json()
    assert len(user) > 0
    assert response.status_code == 200

def test_get_all_users_invalid_token(client):
    access_token = "eyJpZCI6NSwiZXhwIjoxNjc4Njc3NzUwfQ.uyaFKOiuaFCsbG001Hh4uyzikPFGG_ubumwqKiLWUxc.eyJpZCI6NSwiZXhwIjoxNjc4Njc3NzUwfQ"
    client.headers = {**client.headers,"Authorization": f"Bearer {access_token}"}
    response = client.get(f"/users")
    assert response.json().get('detail') == f"Could not validate credentials"
    assert response.status_code == 401

def test_get_all_users_unathorized(client):
    response = client.get(f"/users")
    assert response.json().get('detail') == f"Not authenticated"
    assert response.status_code == 401

def test_user_update(auth_client, test_user):
    response = auth_client.put(f"/users/{test_user['uuid']}", json=user_data)
    new_user = schemas.UserResponse(**response.json())
    assert response.status_code == 202
    assert user_data['email'] == new_user.email


@pytest.mark.parametrize("email, firstname, lastname, username",[
    (fake.email(domain=fake.free_email_domain()),fake.first_name(),fake.last_name(),None),
    (fake.email(domain=fake.free_email_domain()),fake.first_name(),None,None),
    (fake.email(domain=fake.free_email_domain()),None,None,None),
    (None,None,None,None)
])
def test_user_update_missing_body(auth_client,test_user, email, firstname, lastname, username):
    data = {"email":email,"firstname":firstname,"lastname":lastname,"username":username}
    response = auth_client.put(f"/users/{test_user['uuid']}", json=data)
    assert response.status_code == 422


def test_update_user_id_not_exist(auth_client,):
    user_id = "3e04d503-ddd2-4190-914a-bf5e10be8048"
    response = auth_client.put(f"/users/{user_id}", json=user_data)
    assert response.json().get('detail') == f"User with id {user_id} not found"
    assert response.status_code == 404

def test_update_user_invalid_token(client, test_user):
    access_token = "eyJpZCI6NSwiZXhwIjoxNjc4Njc3NzUwfQ.uyaFKOiuaFCsbG001Hh4uyzikPFGG_ubumwqKiLWUxc.eyJpZCI6NSwiZXhwIjoxNjc4Njc3NzUwfQ"
    client.headers = {**client.headers,"Authorization": f"Bearer {access_token}"}
    response = client.put(f"/users/{test_user['uuid']}", json=user_data)
    assert response.json().get('detail') == f"Could not validate credentials"
    assert response.status_code == 401

def test_update_user_unathenticated(client, test_user):
    response = client.put(f"/users/{test_user['uuid']}", json=user_data)
    assert response.json().get('detail') == f"Not authenticated"
    assert response.status_code == 401

def test_user_deletion(auth_client, test_user):
    response = auth_client.delete(f"/users/{test_user['uuid']}")
    assert response.status_code == 204

def test_delete_user_id_not_exist(auth_client):
    user_id = "3e04d503-ddd2-4190-914a-bf5e10be8048"
    response = auth_client.delete(f"/users/{user_id}")
    assert response.json().get('detail') == f"user with id {user_id} not found"
    assert response.status_code == 404

def test_delete_user_invalid_token(client, test_user):
    access_token = "eyJpZCI6NSwiZXhwIjoxNjc4Njc3NzUwfQ.uyaFKOiuaFCsbG001Hh4uyzikPFGG_ubumwqKiLWUxc.eyJpZCI6NSwiZXhwIjoxNjc4Njc3NzUwfQ"
    client.headers = {**client.headers,"Authorization": f"Bearer {access_token}"}
    response = client.delete(f"/users/{test_user['uuid']}")
    assert response.json().get('detail') == f"Could not validate credentials"
    assert response.status_code == 401

def test_delete_user_unathorized(client, test_user):
    response = client.delete(f"/users/{test_user['uuid']}")
    assert response.json().get('detail') == f"Not authenticated"
    assert response.status_code == 401