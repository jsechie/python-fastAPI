from pydantic import BaseSettings

class Settings(BaseSettings):
    # database cred 
    db_hostname: str
    db_password: str
    db_port: str 
    db_name: str 
    db_username: str 

    secret_key: str 
    algorithm: str 
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"


settings = Settings()