from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models import User
from schemas import UserCreate
from utils.hash import hash_password



router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.get("/")
async def read_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.post("/")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    user.password_hash = hash_password(user.password_hash)
    new_user = User(**user.model_dump())
    try:
        db.add(new_user)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        if "users_email_key" in str(e.orig):
            raise HTTPException(status_code=400, detail="Email already registered")
        elif "users_phone_number_key" in str(e.orig):
            raise HTTPException(status_code=400, detail="Phone number already registered")
        elif "users_username_key" in str(e.orig):
            raise HTTPException(status_code=400, detail="Username already taken")
        else:
            raise HTTPException(status_code=500, detail="Internal server error")
    db.refresh(new_user)
    return new_user