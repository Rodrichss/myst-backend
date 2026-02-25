from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from app.core.password_validation import validate_password_strength

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    initials: Optional[str] = None
    picture: Optional[str] = None

    @field_validator('password')
    def validate_password(cls, value: str):
        validate_password_strength(value)
        return value

class UserResponse(BaseModel):
    id_user: int
    name: str
    email: EmailStr
    initials: Optional[str] = None
    picture: Optional[str] = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    initials: Optional[str] = None
    picture: Optional[str] = None