# database.py
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

# Ensure this URL starts with postgresql+asyncpg://
DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")

# 1. Create the Async Engine
engine = create_async_engine(DATABASE_URL, echo=True)

# 2. Create the Async Session Maker
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# 3. Base class for models
class Base(DeclarativeBase):
    pass

# 4. FastAPI Dependency for Database Session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
