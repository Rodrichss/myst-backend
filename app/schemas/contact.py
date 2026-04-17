from pydantic import BaseModel, EmailStr
from typing import Optional

class ContactCreate(BaseModel):
    name: str
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    about = Optional[str] = None
    specialty = Optional[str] = None
    genre =Optional[int] = None

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    about = Optional[str] = None
    specialty = Optional[str] = None
    genre =Optional[int] = None

class ContactResponse(ContactCreate):
    id_contact: int

    class Config:
        from_attributes = True