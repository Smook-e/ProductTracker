from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from base import Base
import os
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# the actual connection to postgres
engine = create_engine(DATABASE_URL)

# factory that creates database sessions
SessionLocal = sessionmaker(bind=engine)


# this runs once at startup and creates all tables
def create_tables():
    # print(DATABASE_URL)
    Base.metadata.create_all(engine)

# opens a db session for each request, closes it after
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
