from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, generate_verification_token, verify_password
from app.core.dependencies import get_current_user, get_db

from app.services.email_service import send_verification_email

from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserDelete,
    UserUpdate,
    UserResponse
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# Create user (public)
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db)
):
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = hash_password(data.password)
    token = generate_verification_token()
    # Create user
    user = User(
        name=data.name,
        email=data.email,
        password=hashed_password,
        initials=data.initials,
        picture=data.picture,
        verification_token=token,
        is_verified=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    try:
        send_verification_email(user.email, token)
    except Exception:
        # manual rollback if email sending fails
        db.delete(user)
        db.commit()
        raise HTTPException(status_code=500, detail="Error enviando correo de verificación")

    return user

# Get current user (private)
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# Update user (private)
@router.patch("/me", response_model=UserResponse)
def update_user(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)
    return current_user

# Delete user (private)
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(
    data: UserDelete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not verify_password(data.password, current_user.password):
        raise HTTPException(
            status_code=400,
            detail="Incorrect password"
        )

    db.delete(current_user)
    db.commit()

    return