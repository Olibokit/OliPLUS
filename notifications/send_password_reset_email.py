import smtplib
from email.message import EmailMessage

RESET_URL_BASE = "https://oliplus.io/reset-password?token="

def send_password_reset_email(email: str, token: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = "🔐 Réinitialisation de votre mot de passe OliPLUS"
    msg["From"] = "no-reply@oliplus.io"
    msg["To"] = email

    reset_link = f"{RESET_URL_BASE}{token}"
    msg.set_content(f"""
Bonjour,

Vous avez demandé une réinitialisation de mot de passe.
Cliquez sur le lien ci-dessous pour définir un nouveau mot de passe :

{reset_link}

Ce lien expirera dans 30 minutes.

Si vous n'avez pas fait cette demande, ignorez ce message.

— Équipe OliPLUS
""")

    # SMTP cockpitifié (à adapter selon ton infra)
    with smtplib.SMTP("smtp.oliplus.io", 587) as server:
        server.starttls()
        server.login("no-reply@oliplus.io", "your-email-password")
        server.send_message(msg)
