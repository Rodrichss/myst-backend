# app/api/schemas/address.py
from pydantic import BaseModel
from typing import Optional


class AddressCreate(BaseModel):
    name: str
    street: str
    neighborhood: Optional[str] = None
    city: str
    state: str
    zip_code: Optional[str] = None
    phone_number: Optional[str] = None
    is_selected: bool = False


class AddressUpdate(BaseModel):
    name: Optional[str] = None
    street: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone_number: Optional[str] = None
    is_selected: Optional[bool] = None


class AddressResponse(BaseModel):
    id_address: int
    id_user: int
    name: str
    street: str
    neighborhood: Optional[str] = None
    city: str
    state: str
    zip_code: Optional[str] = None
    phone_number: Optional[str] = None
    is_selected: bool

    class Config:
        from_attributes = True