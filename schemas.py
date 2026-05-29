from pydantic import BaseModel, EmailStr
from datetime import datetime

class User(BaseModel):
    email: EmailStr | None = None
    phone_number: str | None = None
    username: str

class UserCreate(User):
    password_hash: str
    
class UserRead(User):
    id: int
    created_at: datetime


