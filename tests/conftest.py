from app import schemas
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base
from .database import TestSessionLocal, engine, fake, settings
from jose import JWTError, jwt

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
def test_get_token(client, test_user):
    response = client.post("/login", data={"username":test_user['email'],"password":test_user['password']})
    assert response.json().get('token_type') == "bearer"
    assert response.json().get('expires_in') == "15 minutes"
    token = response.json()
    payload = jwt.decode(token['access_token'], settings.secret_key, algorithms=[settings.algorithm])
    id: str = payload.get("id")
    assert id == test_user['id']
    assert response.status_code == 200
    return token

@pytest.fixture()
def test_user(client):
    user_data = {
            "email":fake.email(domain=fake.free_email_domain()),"firstname":fake.first_name(),
            "lastname":fake.last_name(),"username":fake.user_name(),"password":"Password123"
         }
    response = client.post("/users", json=user_data)
    schemas.UserResponse(**response.json())
    new_user = response.json()
    assert response.status_code == 201
    assert user_data['email'] == new_user['email']
    new_user['password'] = user_data['password']
    return new_user

@pytest.fixture()
def test_post(client, test_get_token):
    post_data = {"title": fake.sentence(), "content": fake.paragraph(), "published": fake.boolean()}
    headers = {"Authorization": f"Bearer {test_get_token['access_token']}"}
    response = client.post("/posts", json=post_data, headers=headers)
    schemas.PostVote(**response.json())
    new_post = response.json()
    assert response.status_code == 201
    assert new_post['Post']['title'] == post_data['title']
    return new_post