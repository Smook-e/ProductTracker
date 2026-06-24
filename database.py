import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool  
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
load_dotenv()

# Async engine/session used by FastAPI request handlers.
DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    poolclass=NullPool,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autoflush=False,
)

class Base(DeclarativeBase):
    pass

# Dependency that yields one async session per request.
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Sync engine/session used by Celery worker tasks.
SYNC_DATABASE_URL = os.getenv("DATABASE_URL")

sync_engine = create_engine(
    SYNC_DATABASE_URL, 
    echo=False,
    pool_pre_ping=True
)

SyncSessionLocal = sessionmaker(bind=sync_engine, expire_on_commit=False)

def get_sync_db():
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()
