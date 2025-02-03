import requests
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import SMTP_SERVER, SMTP_PORT, USERNAME, PASSWORD, FROM_EMAIL, TO_EMAIL, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_email(subject, message):
    """
    Envía un email con el asunto y mensaje indicados en formato HTML.
    """
    msg = MIMEMultipart()
    msg["From"] = FROM_EMAIL
    msg["To"] = TO_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "html"))
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(USERNAME, PASSWORD)
        # Convertir TO_EMAIL a lista (separando por comas y eliminando espacios)
        recipients = [email.strip() for email in TO_EMAIL.split(",")]
        server.sendmail(FROM_EMAIL, recipients, msg.as_string())
        server.quit()
        logging.info("Email enviado correctamente: %s", subject)
    except Exception as e:
        logging.error("Error al enviar el email: %s", e)
        logging.exception(e)

def send_telegram_message(message):
    """
    Envía un mensaje a Telegram usando el Bot API.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"  # Para que se pueda formatear el mensaje con HTML
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logging.info("Mensaje de Telegram enviado correctamente.")
    except Exception as e:
        logging.error("Error al enviar el mensaje a Telegram: %s", e)
        logging.exception(e)
