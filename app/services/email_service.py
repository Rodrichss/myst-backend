import smtplib
from email.mime.text import MIMEText
from app.core.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FRONTEND_URL

def send_verification_email(to_email: str, token: str):

    verification_link = f"{FRONTEND_URL}/auth/verify-email?token={token}"

    subject = "Verifica tu cuenta"
    body = f"""
Hola 👋

Para activar tu cuenta haz clic aquí:

{verification_link}

Si no creaste esta cuenta ignora este mensaje.
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)