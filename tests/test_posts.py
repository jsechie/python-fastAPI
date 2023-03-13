from app import schemas
from .database import fake,settings
from jose import jwt
import pytest

post_data = {"title": fake.sentence(), "content": fake.paragraph(), "published": fake.boolean()}

def test_api_status(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json().get('message') == "API is up and running"

def test_post_creation(auth_client):
    response = auth_client.post("/posts", json=post_data)
    schemas.PostVote(**response.json())
    new_post = response.json()
    assert response.status_code == 201
    assert new_post['Post']['title'] == post_data['title']


def test_create_post_invalid_token(client):
    access_token = "eyJpZCI6NSwiZXhwIjoxNjc4Njc3NzUwfQ.uyaFKOiuaFCsbG001Hh4uyzikPFGG_ubumwqKiLWUxc.eyJpZCI6NSwiZXhwIjoxNjc4Njc3NzUwfQ"
    client.headers = {**client.headers,"Authorization": f"Bearer {access_token}"}
    response = client.post("/posts", json=post_data)
    assert response.json().get('detail') == f"Could not validate credentials"
    assert response.status_code == 401

def test_create_post_unauthorized(client):
    response = client.post("/posts", json=post_data)
    assert response.json().get('detail') == f"Not authenticated"
    assert response.status_code == 401

@pytest.mark.parametrize("title, content, published",[
    (fake.sentence(), fake.paragraph(), None),
    (fake.sentence(), None, None),
    (None, None, None),
])
def test_create_post_missing_body(auth_client, title, content, published):
    post_data = {"title": title, "content": content, "published": published}
    response = auth_client.post("/posts", json=post_data)
    assert response.status_code == 422


def test_get_single_post(auth_client, test_post):
    response = auth_client.get(f"/posts/{test_post['Post']['uuid']}")
    schemas.PostVote(**response.json())
    post = response.json()
    assert post['Post']['uuid'] == test_post['Post']['uuid']
    assert response.status_code == 200

def test_get_single_post_id_not_exist(auth_client):
    post_id = "3e04d503-ddd2-4190-914a-bf5e10be8048"
    response = auth_client.get(f"/posts/{post_id}")
    assert response.json().get('detail') == f"Post with id {post_id} not found"
    assert response.status_code == 404

def test_get_all_posts(auth_client):
    response = auth_client.get(f"/posts")
    posts = response.json()
    assert len(posts) >= 0
    assert response.status_code == 200

def test_post_update(auth_client, test_post,):
    response = auth_client.put(f"/posts/{test_post['Post']['uuid']}", json=post_data)
    new_user = response.json()
    schemas.PostVote(**response.json())
    assert response.status_code == 202
    assert post_data['title'] == new_user['Post']['title']


@pytest.mark.parametrize("title, content, published",[
    (fake.sentence(), None ,None),
    (None, None, None)
])
def test_post_update_missing_body(auth_client,test_post, title, content, published):
    data = {"title":title,"cotent":content,"published":published}
    response = auth_client.put(f"/posts/{test_post['Post']['uuid']}", json=data)
    assert response.status_code == 422


def test_update_post_id_not_exist(auth_client):
    post_id = "3e04d503-ddd2-4190-914a-bf5e10be8048"
    response = auth_client.put(f"/posts/{post_id}", json=post_data)
    assert response.json().get('detail') == f"Post with id {post_id} not found"
    assert response.status_code == 404

def test_update_post_invalid_token(client, test_post):
    access_token = "eyJpZCI6NSwiZXhwIjoxNjc4Njc3NzUwfQ.uyaFKOiuaFCsbG001Hh4uyzikPFGG_ubumwqKiLWUxc.eyJpZCI6NSwiZXhwIjoxNjc4Njc3NzUwfQ"
    client.headers = {**client.headers,"Authorization": f"Bearer {access_token}"}
    response = client.put(f"/posts/{test_post['Post']['uuid']}",json=post_data)
    assert response.json().get('detail') == f"Could not validate credentials"
    assert response.status_code == 401
    

def test_posts_deletion(auth_client, test_post):
    response = auth_client.delete(f"/posts/{test_post['Post']['uuid']}")
    assert response.status_code == 204

def test_delete_post_id_not_exist(auth_client):
    post_id = "3e04d503-ddd2-4190-914a-bf5e10be8048"
    response = auth_client.delete(f"/posts/{post_id}")
    assert response.json().get('detail') == f"Post with id {post_id} not found"
    assert response.status_code == 404

def test_delete_post_invalid_token(client, test_post):
    access_token = "eyJpZCI6NSwiZXhwIjoxNjc4Njc3NzUwfQ.uyaFKOiuaFCsbG001Hh4uyzikPFGG_ubumwqKiLWUxc.eyJpZCI6NSwiZXhwIjoxNjc4Njc3NzUwfQ"
    client.headers = {**client.headers,"Authorization": f"Bearer {access_token}"}
    response = client.delete(f"/posts/{test_post['Post']['uuid']}")
    assert response.json().get('detail') == f"Could not validate credentials"
    assert response.status_code == 401