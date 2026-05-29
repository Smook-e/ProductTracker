from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr | None = None
    phone_number: str | None = None
    username: str
    password_hash: str
    