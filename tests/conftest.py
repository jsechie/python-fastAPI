from app import schemas
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base
from .database import TestSessionLocal, engine, fake
from app.oauth2 import create_access_token

@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

@pytest.fixture()
def token(test_user):
    return create_access_token({'id': test_user['id']})

@pytest.fixture()
def auth_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client

@pytest.fixture()
def test_user(client):
    user_data = {
            "email":fake.email(domain=fake.free_email_domain()),"firstname":fake.first_name(),
            "lastname":fake.last_name(),"username":fake.user_name(),"password":"Password123"
         }
    response = client.post("/users", json=user_data)
    new_user = response.json()
    assert response.status_code == 201
    new_user['password'] = user_data['password']
    return new_user

@pytest.fixture()
def test_post(auth_client):
    post_data = {"title": fake.sentence(), "content": fake.paragraph(), "published": fake.boolean()}
    response = auth_client.post("/posts", json=post_data)
    schemas.PostVote(**response.json())
    new_post = response.json()
    assert response.status_code == 201
    return new_post