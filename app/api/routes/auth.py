from datetime import datetime, timedelta
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Query, Form
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.assets.colors import PRIMARY, SECONDARY, LIGHT, DARK

from app.db.database import SessionLocal
from app.models.password_reset import PasswordResetToken
from app.models.user import User
from app.schemas.auth import Token, ForgotPasswordRequest
from app.services.email_service import send_reset_password_email, send_verification_email
from app.core.security import hash_password, verify_password, create_access_token, generate_verification_token
from app.core.password_validation import validate_password_strength

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

    def render_page(title, message, type="success"):
        return HTMLResponse(f"""
        <html>
        <head>
            <style>
                :root {{
                    --primary: {PRIMARY};
                    --secondary: {SECONDARY};
                    --light: {LIGHT};
                    --dark: {DARK};

                    --success: #6FCF97;
                    --warning: #F2C94C;
                    --error: #C06C84;
                }}

                body {{
                    margin: 0;
                    padding: 0;
                    font-family: 'Segoe UI', sans-serif;
                    background: linear-gradient(135deg, var(--primary), var(--secondary));
                    height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }}

                .container {{
                    background: var(--light);
                    padding: 40px;
                    border-radius: 16px;
                    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
                    width: 100%;
                    max-width: 400px;
                    text-align: center;
                }}

                .logo {{
                    font-size: 22px;
                    font-weight: bold;
                    color: var(--primary);
                    margin-bottom: 15px;
                }}

                h2 {{
                    color: var(--dark);
                    margin-bottom: 10px;
                }}

                p {{
                    font-size: 14px;
                    margin-bottom: 20px;
                    color: #666;
                }}

                .status {{
                    font-weight: bold;
                    margin-top: 10px;
                }}

                .success {{ color: var(--success); }}
                .warning {{ color: var(--warning); }}
                .error {{ color: var(--error); }}

                a {{
                    display: inline-block;
                    margin-top: 15px;
                    padding: 10px 15px;
                    border-radius: 10px;
                    background: var(--primary);
                    color: white;
                    text-decoration: none;
                    font-size: 14px;
                    transition: 0.3s;
                }}

                a:hover {{
                    background: var(--secondary);
                }}
            </style>
        </head>

        <body>
            <div class="container">
                <div class="logo">Myst</div>
                <h2 class="status {type}">{title}</h2>
                <p>{message}</p>
            </div>
        </body>
        </html>
        """)

    if not user:
        return render_page(
            "Enlace inválido",
            "El enlace de verificación no es válido o ha expirado.",
            "error"
        )

    if user.is_verified:
        return render_page(
            "Correo ya verificado",
            "Tu cuenta ya estaba verificada. Puedes iniciar sesión sin problema.",
            "warning"
        )

    user.is_verified = True
    user.verification_token = None

    db.commit()

    return render_page(
        "¡Correo verificado!",
        "Tu cuenta ha sido verificada correctamente. Ya puedes iniciar sesión.",
        "success"
    )

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

        ahora = datetime.utcnow()
        if user.last_verification_sent and ahora < user.last_verification_sent + timedelta(minutes=2):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Por favor, espera 2 minutos antes de solicitar otro correo de verificación."
            )
        
        new_token = generate_verification_token()
        user.verification_token = new_token
        user.last_verification_sent = ahora
        
        db.commit()

        try:
            send_verification_email(user.email, new_token)
            
            # Lanzamos 403: Forbidden (Entendido, pero prohibido por falta de verificación)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email not verified. Se ha enviado un nuevo enlace de activación."
            )
        except Exception:
            # Si SendGrid falla aquí, no borramos al usuario (a diferencia de create_user)
            # porque el usuario ya tiene su cuenta, solo le avisamos del error de envío.
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email not verified. Error al reenviar correo, intenta más tarde."
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
    validate_password_strength(new_password)

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

    if not user.is_verified:
        user.is_verified = True
        user.verification_token = None

    db.delete(reset)
    db.commit()

    return {"message": "Contraseña actualizada correctamente"}

# formulario de restablecer contraseña
@router.get("/reset-password", response_class=HTMLResponse)
def reset_password_form(token: str):

    return f"""
    <html>
    <head>
        <style>
            :root {{
                --primary: {PRIMARY};
                --secondary: {SECONDARY};
                --light: {LIGHT};
                --dark: {DARK};

                /* colores suaves */
                --error: #C06C84;      /* rojo suave */
                --success: #6FCF97;    /* verde suave */
            }}

            body {{
                margin: 0;
                padding: 0;
                font-family: 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, var(--primary), var(--secondary));
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }}

            .container {{
                background: var(--light);
                padding: 40px;
                border-radius: 16px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.15);
                width: 100%;
                max-width: 400px;
                text-align: center;
            }}

            h2 {{
                color: var(--dark);
            }}

            p {{
                color: #666;
                font-size: 14px;
                margin-bottom: 20px;
            }}

            .input-group {{
                position: relative;
                margin-bottom: 15px;
            }}

            input {{
                width: 100%;
                padding: 12px;
                border-radius: 10px;
                border: 1px solid #ccc;
                font-size: 14px;
            }}

            input:focus {{
                outline: none;
                border-color: var(--primary);
                box-shadow: 0 0 5px var(--primary);
            }}

            .toggle {{
                position: absolute;
                right: 10px;
                top: 50%;
                transform: translateY(-50%);
                cursor: pointer;
                font-size: 12px;
                color: var(--primary);
            }}

            .rules {{
                text-align: left;
                font-size: 12px;
                margin-bottom: 10px;
            }}

            .rules span {{
                display: block;
                margin-bottom: 4px;
                color: #999;
            }}

            .rules span.valid {{
                color: var(--success);
            }}

            .rules span.invalid {{
                color: var(--error);
            }}

            button {{
                width: 100%;
                padding: 12px;
                border: none;
                border-radius: 10px;
                background: var(--primary);
                color: white;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: 0.3s;
                opacity: 0.6;
            }}

            button.enabled {{
                opacity: 1;
            }}

            button:disabled {{
                cursor: not-allowed;
            }}

            .logo {{
                font-size: 22px;
                font-weight: bold;
                color: var(--primary);
                margin-bottom: 15px;
            }}
        </style>
    </head>

    <body>
        <div class="container">
            <div class="logo">Myst</div>
            <h2>Restablecer contraseña</h2>
            <p>Tu contraseña debe cumplir con los requisitos</p>

            <form id="form" action="/auth/reset-password" method="post">
                <input type="hidden" name="token" value="{token}" />

                <div class="input-group">
                    <input type="password" id="password" name="new_password" placeholder="Nueva contraseña" required>
                    <span class="toggle" onclick="togglePassword('password')">👁</span>
                </div>

                <div class="input-group">
                    <input type="password" id="confirm" placeholder="Confirmar contraseña" required>
                    <span class="toggle" onclick="togglePassword('confirm')">👁</span>
                </div>

                <div class="rules">
                    <span id="length">• Mínimo 8 caracteres</span>
                    <span id="upper">• Al menos una mayúscula</span>
                    <span id="lower">• Al menos una minúscula</span>
                    <span id="digit">• Al menos un número</span>
                    <span id="special">• Al menos un carácter especial</span>
                    <span id="match">• Las contraseñas coinciden</span>
                </div>

                <button id="submitBtn" type="submit" disabled>Cambiar contraseña</button>
            </form>
        </div>

        <script>
            const password = document.getElementById('password');
            const confirm = document.getElementById('confirm');
            const button = document.getElementById('submitBtn');

            const rules = {{
                length: document.getElementById('length'),
                upper: document.getElementById('upper'),
                lower: document.getElementById('lower'),
                digit: document.getElementById('digit'),
                special: document.getElementById('special'),
                match: document.getElementById('match')
            }};

            function togglePassword(id) {{
                const input = document.getElementById(id);
                input.type = input.type === "password" ? "text" : "password";
            }}

            function validate() {{
                const pass = password.value;
                const conf = confirm.value;

                const checks = {{
                    length: pass.length >= 8,
                    upper: /[A-Z]/.test(pass),
                    lower: /[a-z]/.test(pass),
                    digit: /[0-9]/.test(pass),
                    special: /[!@#$%^&*(),.?":{{}}|<>]/.test(pass),
                    match: pass && conf && pass === conf
                }};

                let allValid = true;

                for (let key in checks) {{
                    if (checks[key]) {{
                        rules[key].classList.add("valid");
                        rules[key].classList.remove("invalid");
                    }} else {{
                        rules[key].classList.add("invalid");
                        rules[key].classList.remove("valid");
                        allValid = false;
                    }}
                }}

                button.disabled = !allValid;
                if (allValid) button.classList.add("enabled");
                else button.classList.remove("enabled");
            }}

            password.addEventListener('input', validate);
            confirm.addEventListener('input', validate);
        </script>
    </body>
    </html>
    """