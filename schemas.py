from pydantic import BaseModel, EmailStr
from datetime import datetime
from models import NotificationChannel

class User(BaseModel):
    email: EmailStr | None = None
    phone_number: str | None = None
    username: str
    notification_channel: NotificationChannel | None = None

class UserCreate(User):
    password_hash: str
    
class UserRead(User):
    id: int
    created_at: datetime

    
    class Config:
        orm_mode = True


