from typing import List
from app import schemas
from .database import fake,settings
from jose import JWTError, jwt
import pytest

user_data = {
            "email":fake.email(domain=fake.free_email_domain()),"firstname":fake.first_name(),
            "lastname":fake.last_name(),"username":fake.user_name(),"password":"Password123"
         }

def test_connection(client):
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
    data = {
            "email":email,"firstname":firstname,"lastname":lastname,"username":username,"password":password
         }
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


def test_get_single_user(client, test_get_token, test_user):
    headers = {"Authorization": f"Bearer {test_get_token['access_token']}"}
    response = client.get(f"/users/{test_user['uuid']}", headers=headers)
    user = schemas.UserResponse(**response.json())
    assert user.uuid == test_user['uuid']
    assert test_get_token['expires_in'] == "15 minutes"
    assert test_get_token['token_type'] == "bearer"
    assert response.status_code == 200


def test_get_single_user_id_not_exist(client, test_get_token):
    headers = {"Authorization": f"Bearer {test_get_token['access_token']}"}
    user_id = "3e04d503-ddd2-4190-914a-bf5e10be8048"
    response = client.get(f"/users/{user_id}", headers=headers)
    assert response.json().get('detail') == f"User with id {user_id} not found"
    assert test_get_token['expires_in'] == "15 minutes"
    assert test_get_token['token_type'] == "bearer"
    assert response.status_code == 404

def test_get_single_user_invalid_token(client, test_user):
    access_token = "eyJpZCI6NSwiZXhwIjoxNjc4Njc3NzUwfQ.uyaFKOiuaFCsbG001Hh4uyzikPFGG_ubumwqKiLWUxc"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get(f"/users/{test_user['uuid']}", headers=headers)
    assert response.json().get('detail') == f"Could not validate credentials"
    assert response.status_code == 401

def test_get_all_users(client, test_get_token):
    headers = {"Authorization": f"Bearer {test_get_token['access_token']}"}
    response = client.get(f"/users", headers=headers)
    user = response.json()
    assert test_get_token['expires_in'] == "15 minutes"
    assert test_get_token['token_type'] == "bearer"
    assert len(user) > 0
    assert response.status_code == 200

def test_get_all_users_invalid_token(client):
    access_token = "eyJpZCI6NSwiZXhwIjoxNjc4Njc3NzUwfQ.uyaFKOiuaFCsbG001Hh4uyzikPFGG_ubumwqKiLWUxc"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get(f"/users", headers=headers)
    assert response.json().get('detail') == f"Could not validate credentials"
    assert response.status_code == 401

def test_user_update(client, test_user, test_get_token):
    headers = {"Authorization": f"Bearer {test_get_token['access_token']}"}
    response = client.put(f"/users/{test_user['uuid']}", json=user_data, headers=headers)
    new_user = schemas.UserResponse(**response.json())
    assert response.status_code == 202
    assert user_data['email'] == new_user.email


@pytest.mark.parametrize("email, firstname, lastname, username",[
    (fake.email(domain=fake.free_email_domain()),fake.first_name(),fake.last_name(),None),
    (fake.email(domain=fake.free_email_domain()),fake.first_name(),None,None),
    (fake.email(domain=fake.free_email_domain()),None,None,None),
    (None,None,None,None)
])
def test_user_update_missing_body(client,test_user, test_get_token, email, firstname, lastname, username):
    data = {
            "email":email,"firstname":firstname,"lastname":lastname,"username":username
         }
    headers = {"Authorization": f"Bearer {test_get_token['access_token']}"}
    response = client.put(f"/users/{test_user['uuid']}", headers=headers, json=data)
    assert response.status_code == 422


def test_update_user_id_not_exist(client, test_get_token):
    headers = {"Authorization": f"Bearer {test_get_token['access_token']}"}
    user_id = "3e04d503-ddd2-4190-914a-bf5e10be8048"
    response = client.put(f"/users/{user_id}", headers=headers, json=user_data)
    assert response.json().get('detail') == f"User with id {user_id} not found"
    assert test_get_token['expires_in'] == "15 minutes"
    assert test_get_token['token_type'] == "bearer"
    assert response.status_code == 404

def test_update_user_invalid_token(client, test_user):
    access_token = "eyJpZCI6NSwiZXhwIjoxNjc4Njc3NzUwfQ.uyaFKOiuaFCsbG001Hh4uyzikPFGG_ubumwqKiLWUxc"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.put(f"/users/{test_user['uuid']}", headers=headers, json=user_data)
    assert response.json().get('detail') == f"Could not validate credentials"
    assert response.status_code == 401

def test_user_deletion(client, test_user, test_get_token):
    headers = {"Authorization": f"Bearer {test_get_token['access_token']}"}
    response = client.delete(f"/users/{test_user['uuid']}", headers=headers)
    assert response.status_code == 204

def test_delete_user_id_not_exist(client, test_get_token):
    headers = {"Authorization": f"Bearer {test_get_token['access_token']}"}
    user_id = "3e04d503-ddd2-4190-914a-bf5e10be8048"
    response = client.delete(f"/users/{user_id}", headers=headers)
    assert response.json().get('detail') == f"user with id {user_id} not found"
    assert test_get_token['expires_in'] == "15 minutes"
    assert test_get_token['token_type'] == "bearer"
    assert response.status_code == 404

def test_delete_user_invalid_token(client, test_user):
    access_token = "eyJpZCI6NSwiZXhwIjoxNjc4Njc3NzUwfQ.uyaFKOiuaFCsbG001Hh4uyzikPFGG_ubumwqKiLWUxc"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.delete(f"/users/{test_user['uuid']}", headers=headers)
    assert response.json().get('detail') == f"Could not validate credentials"
    assert response.status_code == 401