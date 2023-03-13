import time
import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from faker import Faker

fake = Faker()

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.test_db_username}:{settings.test_db_password}@{settings.test_db_hostname}/{settings.test_db_name}"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

while True: 
    try:
        # Connect to your postgres DB
        conn = psycopg2.connect(host=settings.test_db_hostname,database=settings.test_db_name,
                                user=settings.test_db_username,password=settings.test_db_password,
                                cursor_factory=RealDictCursor
                            )
        cursor = conn.cursor()
        print("Connected to test database made successfully")
        # enable uuid v4 generator extension
        cursor.execute("""CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"""")
        conn.commit()
        print("uuid_ossp extension installed")
        break
    except Exception as error:
        print("Connection to database failed")
        print("Error: ",error)
        time.sleep(3)
