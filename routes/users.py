from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserCreate




router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.get("/")
async def read_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.post("/")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    user.pas
    user = User(**user.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user