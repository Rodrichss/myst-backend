from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import hash_password

from app.db.database import SessionLocal
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=UserResponse)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db)
):
    hashed_password = hash_password(data.password)
    user = User(
        name=data.name,
        email=data.email,
        password=hashed_password,
        initials=data.initials,
        picture=data.picture
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/{id_user}", response_model=UserResponse)
def get_user(
    id_user: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id_user == id_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{id_user}", response_model=UserResponse)
def update_user(
    id_user: int,
    data: UserUpdate,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id_user == id_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user

@router.get("/", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()