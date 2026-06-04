from pydantic import BaseModel, EmailStr, HttpUrl
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
        from_attributes = True

class ProductScrapeRequest(BaseModel):
    url: HttpUrl

class ProductScrapeResponse(BaseModel):
    title: str
    
    image_url: str
    source: str
    url: str

class PriceHistoryRead(BaseModel):
    price: int
    recorded_at: datetime

    class Config:
        from_attributes = True

class ProductRead(ProductScrapeResponse):
    id: int
    created_at: datetime
    next_scrape: datetime
    price_histories: list[PriceHistoryRead] = []
    user_count: int = 0

    class Config:
        from_attributes = True