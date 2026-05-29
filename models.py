
from datetime import datetime

from sqlalchemy import Enum, ForeignKey, func, TIMESTAMP, Numeric, orm
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from base import Base


class NotificationChannel(enum.Enum):
    email = "email"
    sms = "sms"

class ProductSource(enum.Enum):
    amazon = "amazon"
    other = "other"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(unique=True) # nullable=False is automatic for str
    email: Mapped[str | None] = mapped_column(unique=True) # None means nullable=True
    phone_number: Mapped[str | None] = mapped_column(unique=True)
    password_hash: Mapped[str] = mapped_column()
    notification_channel: Mapped[NotificationChannel | None] = mapped_column(Enum(NotificationChannel))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column()
    asin: Mapped[str] = mapped_column(unique=True)
    url: Mapped[str] = mapped_column()
    image_url: Mapped[str | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    source: Mapped[ProductSource] = mapped_column(Enum(ProductSource), nullable=False)

class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    
    
    price: Mapped[int] = mapped_column() 
    recorded_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    


class UserProduct(Base):
    __tablename__ = "user_products"

    # id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True)
    added_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    
    
    
