import time
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.db_username}:{settings.db_password}@{settings.db_hostname}/{settings.db_name}"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

while True: 
    try:
        # Connect to your postgres DB
        conn = psycopg2.connect(host=settings.db_hostname,
                                database=settings.db_name,
                                user=settings.db_username,
                                password=settings.db_password,
                                cursor_factory=RealDictCursor
                            )
        cursor = conn.cursor()
        print("Connection to database made successfully")
        break
    except Exception as error:
        print("Connection to database failed")
        print("Error: ",error)
        time.sleep(3)