from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

# Async imports
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import User
from schemas import UserCreate, UserRead, User as UserSchema
from utils.hash import hash_password

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/", response_model=list[UserRead])
async def read_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserRead)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Hash password
    user.password_hash = hash_password(user.password_hash)
    new_user = User(**user.model_dump())
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError as e:
        await db.rollback()
        if "users_email_key" in str(e.orig):
            raise HTTPException(status_code=400, detail="Email already registered")
        elif "users_phone_number_key" in str(e.orig):
            raise HTTPException(status_code=400, detail="Phone number already registered")
        elif "users_username_key" in str(e.orig):
            raise HTTPException(status_code=400, detail="Username already taken")
        else:
            raise HTTPException(status_code=500, detail="Internal server error")
    
    return new_user


@router.get("/{user_id}", response_model=UserRead)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.delete(user)
    await db.commit()


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int, 
    user_update: UserSchema, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        if key == "password_hash" and value:
            setattr(user, key, hash_password(value))
        else:
            setattr(user, key, value)

    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError as e:
        await db.rollback()
        error_str = str(e.orig) if e.orig else str(e)
        
        if "users_email_key" in error_str:
            raise HTTPException(status_code=400, detail="Email already registered")
        elif "users_phone_number_key" in error_str:
            raise HTTPException(status_code=400, detail="Phone number already registered")
        elif "users_username_key" in error_str:
            raise HTTPException(status_code=400, detail="Username already taken")
        else:
            raise HTTPException(status_code=500, detail="Internal server error")
    
    return user