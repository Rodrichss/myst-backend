from datetime import datetime, timedelta
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Query, Form
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.password_reset import PasswordResetToken
from app.models.user import User
from app.schemas.auth import ResetPasswordRequest, Token, ForgotPasswordRequest
from app.services.email_service import send_reset_password_email
from app.core.security import hash_password, verify_password, create_access_token

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

# olvidé mi contraseña
@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(404, "Usuario no encontrado")

    token = str(uuid.uuid4())

    reset = PasswordResetToken(
        user_id=user.id_user,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )

    db.add(reset)
    db.commit()

    # enviar correo con link
    send_reset_password_email(user.email, token)

    return {"message": "Se envió correo para restablecer contraseña"}

# restablecer contraseña
@router.post("/reset-password")
def reset_password(
    token: str = Form(...),
    new_password: str = Form(...),
    db: Session = Depends(get_db)
):

    # Buscar el token en la base de datos
    reset = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token
    ).first()

    if not reset:
        raise HTTPException(
            status_code=400,
            detail="Token inválido"
        )

    # Verificar si el token expiró
    if reset.expires_at < datetime.utcnow():
        db.delete(reset)
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="Token expirado"
        )

    # Buscar al usuario asociado al token
    user = db.query(User).filter(
        User.id_user == reset.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    user.password = hash_password(new_password)

    db.delete(reset)
    db.commit()

    return {"message": "Contraseña actualizada correctamente"}

# formulario de restablecer contraseña
@router.get("/reset-password", response_class=HTMLResponse)
def reset_password_form(token: str):

    return f"""
    <html>
        <body>
            <h2>Restablecer contraseña</h2>

            <form action="/auth/reset-password" method="post">
                <input type="hidden" name="token" value="{token}" />

                <label>Nueva contraseña:</label><br>
                <input type="password" name="new_password" required><br><br>

                <button type="submit">Cambiar contraseña</button>
            </form>

        </body>
    </html>
    """

