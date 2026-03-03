import smtplib
from email.mime.text import MIMEText
from app.core.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FRONTEND_URL

color_primary = "#4F338A"
color_secondary = "#8270AA"
color_background = "#ECECEC"

def send_verification_email(to_email: str, token: str):
    verification_link = f"{FRONTEND_URL}/auth/verify-email?token={token}"

    subject = "Verifica tu cuenta"
    body = f"""
<html>
    <body style="margin:0; padding:0; font-family:'Montserrat', Arial, Helvetica, sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
            <td align="center">
            <table width="600" cellpadding="20" cellspacing="0" style="background-color:{color_background}; border-radius:8px;">
                <tr>
                <td>

                    <h2 style="color:{color_primary}; margin-top:0;">
                    Bienvenida a Myst ✨
                    </h2>

                    <p style="font-size:14px;">Gracias por registrarte en <strong>Myst</strong>.</p>

                    <p style="font-size:14px;">
                    Myst es tu espacio seguro para gestionar tu bienestar y tu información personal.
                    </p>

                    <p style="text-align:center; margin:30px 0;">
                    <a href="{verification_link}"
                        style="background-color:{color_primary};
                                color:white;
                                padding:12px 24px;
                                text-decoration:none;
                                border-radius:6px;
                                font-weight:600;">
                        Verificar cuenta
                    </a>
                    </p>

                    <p style="font-size:14px;">
                    Este enlace expirará en 30 minutos.
                    </p>

                    <hr style="border:none; border-top:1px solid {color_secondary};">

                    <p style="font-size:12px; color:gray;">
                    Si no creaste esta cuenta, ignora este mensaje.<br>
                    El equipo de Myst ✨
                    </p>

                </td>
                </tr>
            </table>
            </td>
        </tr>
        </table>
    </body>
</html>
"""

    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = f"Myst <{SMTP_USER}>"
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

def send_reset_password_email(to_email: str, token: str):

    reset_link = f"{FRONTEND_URL}/auth/reset-password?token={token}"

    subject = "Restablece tu contraseña"
    body = f"""
<html>
    <body style="margin:0; padding:0; font-family:'Montserrat', Arial, Helvetica, sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
            <td align="center">
            <table width="600" cellpadding="20" cellspacing="0" style="background-color:{color_background}; border-radius:8px;">
                <tr>
                <td>

                    <h2 style="color:{color_primary}; margin-top:0;">
                    Restablece tu contraseña 🔐
                    </h2>

                    <p style="font-size:14px;">
                    Recibimos una solicitud para restablecer la contraseña de tu cuenta en <strong>Myst</strong>.
                    </p>

                    <p style="font-size:14px;">
                    Myst es tu espacio seguro para gestionar tu bienestar y tu información personal de forma privada.
                    </p>

                    <p style="text-align:center; margin:30px 0;">
                    <a href="{reset_link}"
                        style="background-color:{color_primary};
                                color:white;
                                padding:12px 24px;
                                text-decoration:none;
                                border-radius:6px;
                                font-weight:600;">
                        Restablecer contraseña
                    </a>
                    </p>

                    <p style="font-size:14px;">
                    Este enlace expirará en 30 minutos por motivos de seguridad.
                    </p>

                    <hr style="border:none; border-top:1px solid {color_secondary};">

                    <p style="font-size:12px; color:gray;">
                    Si no solicitaste este cambio, puedes ignorar este mensaje. Tu cuenta seguirá segura.<br><br>
                    El equipo de Myst ✨<br>
                    Myst nunca te pedirá tu contraseña por correo electrónico.
                    </p>

                </td>
                </tr>
            </table>
            </td>
        </tr>
        </table>
    </body>
</html>
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = f"Myst <{SMTP_USER}>"
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)