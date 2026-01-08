from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    initials: Optional[str] = None
    picture: Optional[str] = None

class UserResponse(BaseModel):
    id_user: int
    name: str
    email: EmailStr
    initials: Optional[str] = None
    picture: Optional[str] = None

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    initials: Optional[str] = None
    picture: Optional[str] = None