from sqlalchemy import select

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models import User

from utils.hash import verify_password, dummy_hash
from utils.oauth2 import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/login")
async def login(user_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    print(f"Login attempt for username: {user_data.username}")
    db_user = await db.execute(select(User).where(
        (User.username == user_data.username) |
        (User.email == user_data.username)
    ))
    db_user = db_user.scalar_one_or_none()
    if not db_user:
        verify_password(user_data.password, dummy_hash)
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not verify_password(user_data.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    payload = {"user_id": str(db_user.id), "username": db_user.username}
    token = create_access_token(payload)
    print(f"User {db_user.username} logged in, token: {token}")
    return {"access_token": token, "token_type": "bearer"}