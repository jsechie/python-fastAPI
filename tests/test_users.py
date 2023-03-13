from app import schemas
from faker import Faker
from .database import client, session

# Create a Faker object
fake = Faker()


def test_connection(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json().get('message') == "API is up and running"

def test_user_creation(client):
    data = {
            "email":fake.email(domain=fake.free_email_domain()),"firstname":fake.first_name(),
            "lastname":fake.last_name(),"username":fake.user_name(),"password":"Password123"
         }
    response = client.post("/users", 
                           json=data
                        )
    new_user = schemas.UserResponse(**response.json())
    assert response.status_code == 201
    assert data['email'] == new_user.email

def test_user_login(client):
    payload = {
            "email":fake.email(domain=fake.free_email_domain()),"firstname":fake.first_name(),
            "lastname":fake.last_name(),"username":fake.user_name(),"password":"Password123"
         }
    response = client.post("/users", json=payload)
    new_user = schemas.UserResponse(**response.json())
    assert response.status_code == 201
    assert payload['email'] == new_user.email
    response = client.post("/login", data={"username":payload['email'],"password":payload['password']})
    token = schemas.Token(**response.json())
    assert token.token_type == "bearer"
    assert token.expires_in == "15 minutes"
    assert response.status_code == 200
