from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models import User

from utils.hash import verify_password, dummy_hash
from utils.oauth2 import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/login")
async def login(user_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(
        (User.username == user_data.username) |
        (User.email == user_data.username) 
    ).first()
    if not db_user:
        verify_password(user_data.password, dummy_hash)
        return HTTPException(status_code=400, detail="Invalid credentials")
    if not verify_password(user_data.password, db_user.password_hash):
        return HTTPException(status_code=400, detail="Invalid credentials")
    payload = {"user_id": str(db_user.id), "username": db_user.username}
    token = create_access_token(payload)
    return {"access_token": token, "token_type": "bearer"}