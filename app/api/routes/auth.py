from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.user import User
from app.schemas.auth import Token
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

# verificar correo
@router.get("/verify-email")
def verify_email(token: str = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()

    if not user:
        raise HTTPException(status_code=404, detail="Invalid verification token")

    if user.is_verified:
        return HTMLResponse("<h2>Email already verified</h2>")

    user.is_verified = True
    user.verification_token = None

    db.commit()

    return HTMLResponse("<h2>Email verified successfully</h2>")

# ingresar
@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # OAuth2 usa "username", nosotros usamos email
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )

    access_token = create_access_token(
        data={"sub": str(user.id_user)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
