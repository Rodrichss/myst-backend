from pydantic import BaseModel, EmailStr, field_validator
from app.core.password_validation import validate_password_strength

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator('new_password')
    def validate_password(cls, value: str):
        validate_password_strength(value)
        return value