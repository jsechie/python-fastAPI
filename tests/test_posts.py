from app import schemas
from .database import fake,settings
from jose import jwt
import pytest

post_data = {"title": fake.sentence(), "content": fake.paragraph(), "published": fake.boolean()}

def test_api_status(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json().get('message') == "API is up and running"

def test_post_creation(client,test_get_token):
    headers = {"Authorization": f"Bearer {test_get_token['access_token']}"}
    response = client.post("/posts", json=post_data, headers=headers)
    schemas.PostVote(**response.json())
    new_post = response.json()
    assert response.status_code == 201
    assert new_post['Post']['title'] == post_data['title']

def test_create_post_invalid_token(client):
    access_token = "eyJpZCI6NSwiZXhwIjoxNjc4Njc3NzUwfQ.uyaFKOiuaFCsbG001Hh4uyzikPFGG_ubumwqKiLWUxc"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/posts", json=post_data, headers=headers)
    assert response.json().get('detail') == f"Could not validate credentials"
    assert response.status_code == 401

@pytest.mark.parametrize("title, content, published",[
    (fake.sentence(), fake.paragraph(), None),
    (fake.sentence(), None, None),
    (None, None, None),
])
def test_create_post_missing_body(client,test_get_token, title, content, published):
    post_data = {"title": title, "content": content, "published": published}
    headers = {"Authorization": f"Bearer {test_get_token['access_token']}"}
    response = client.post("/posts", json=post_data, headers=headers)
    assert response.status_code == 422


def test_get_single_post(client, test_get_token, test_post):
    headers = {"Authorization": f"Bearer {test_get_token['access_token']}"}
    response = client.get(f"/posts/{test_post['Post']['uuid']}", headers=headers)
    schemas.PostVote(**response.json())
    post = response.json()
    assert post['Post']['uuid'] == test_post['Post']['uuid']
    assert test_get_token['expires_in'] == "15 minutes"
    assert test_get_token['token_type'] == "bearer"
    assert response.status_code == 200

def test_get_single_post_id_not_exist(client, test_get_token):
    headers = {"Authorization": f"Bearer {test_get_token['access_token']}"}
    post_id = "3e04d503-ddd2-4190-914a-bf5e10be8048"
    response = client.get(f"/posts/{post_id}", headers=headers)
    assert response.json().get('detail') == f"Post with id {post_id} not found"
    assert test_get_token['expires_in'] == "15 minutes"
    assert test_get_token['token_type'] == "bearer"
    assert response.status_code == 404

def test_get_all_posts(client, test_get_token):
    headers = {"Authorization": f"Bearer {test_get_token['access_token']}"}
    response = client.get(f"/posts", headers=headers)
    posts = response.json()
    assert test_get_token['expires_in'] == "15 minutes"
    assert test_get_token['token_type'] == "bearer"
    assert len(posts) >= 0
    assert response.status_code == 200

def test_post_update(client, test_post, test_get_token):
    headers = {"Authorization": f"Bearer {test_get_token['access_token']}"}
    response = client.put(f"/posts/{test_post['Post']['uuid']}", json=post_data, headers=headers)
    new_user = response.json()
    schemas.PostVote(**response.json())
    assert response.status_code == 202
    assert post_data['title'] == new_user['Post']['title']


@pytest.mark.parametrize("title, content, published",[
    (fake.sentence(), None ,None),
    (None, None, None)
])
def test_post_update_missing_body(client,test_post, test_get_token, title, content, published):
    data = {
            "title":title,"cotent":content,"published":published
         }
    headers = {"Authorization": f"Bearer {test_get_token['access_token']}"}
    response = client.put(f"/posts/{test_post['Post']['uuid']}", headers=headers, json=data)
    assert response.status_code == 422


def test_update_post_id_not_exist(client, test_get_token):
    headers = {"Authorization": f"Bearer {test_get_token['access_token']}"}
    post_id = "3e04d503-ddd2-4190-914a-bf5e10be8048"
    response = client.put(f"/posts/{post_id}", headers=headers, json=post_data)
    assert response.json().get('detail') == f"Post with id {post_id} not found"
    assert test_get_token['expires_in'] == "15 minutes"
    assert test_get_token['token_type'] == "bearer"
    assert response.status_code == 404

def test_update_user_invalid_token(client, test_post):
    access_token = "eyJpZCI6NSwiZXhwIjoxNjc4Njc3NzUwfQ.uyaFKOiuaFCsbG001Hh4uyzikPFGG_ubumwqKiLWUxc"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.put(f"/users/{test_post['Post']['uuid']}", headers=headers, json=post_data)
    assert response.json().get('detail') == f"Could not validate credentials"
    assert response.status_code == 401

def test_posts_deletion(client, test_post, test_get_token):
    headers = {"Authorization": f"Bearer {test_get_token['access_token']}"}
    response = client.delete(f"/posts/{test_post['Post']['uuid']}", headers=headers)
    assert response.status_code == 204

def test_delete_post_id_not_exist(client, test_get_token):
    headers = {"Authorization": f"Bearer {test_get_token['access_token']}"}
    post_id = "3e04d503-ddd2-4190-914a-bf5e10be8048"
    response = client.delete(f"/posts/{post_id}", headers=headers)
    assert response.json().get('detail') == f"Post with id {post_id} not found"
    assert test_get_token['expires_in'] == "15 minutes"
    assert test_get_token['token_type'] == "bearer"
    assert response.status_code == 404

def test_delete_post_invalid_token(client, test_post):
    access_token = "eyJpZCI6NSwiZXhwIjoxNjc4Njc3NzUwfQ.uyaFKOiuaFCsbG001Hh4uyzikPFGG_ubumwqKiLWUxc"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.delete(f"/posts/{test_post['Post']['uuid']}", headers=headers)
    assert response.json().get('detail') == f"Could not validate credentials"
    assert response.status_code == 401