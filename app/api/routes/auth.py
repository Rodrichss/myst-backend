from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.user import User
from app.schemas.auth import Token, LoginRequest
from app.core.security import verify_password, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_access_token(
        data={"sub": str(user.id_user)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
