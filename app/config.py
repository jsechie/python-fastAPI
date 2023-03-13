from pydantic import BaseSettings

class Settings(BaseSettings):
    # database cred 
    db_hostname: str
    db_password: str
    db_port: str 
    db_name: str 
    db_username: str 

    # test database credential
    test_db_hostname: str
    test_db_password: str
    test_db_port: str 
    test_db_name: str 
    test_db_username: str

    secret_key: str 
    algorithm: str 
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"


settings = Settings()