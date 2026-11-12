"""Envío de mails por SMTP, o a archivos .html si SMTP no está configurado."""
import logging
import re
import smtplib
import ssl
from datetime import datetime
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path

from .config import settings

log = logging.getLogger("atucasa.email")


def smtp_configurado() -> bool:
    return bool(settings.SMTP_HOST)


def enviar_correo(destinatario: str, asunto: str, html: str, texto: str) -> None:
    """Envía un mail. Nunca lanza excepciones: un mail que falla no debe romper un pedido."""
    try:
        if smtp_configurado():
            _enviar_smtp(destinatario, asunto, html, texto)
            log.info("Mail enviado a %s: %s", destinatario, asunto)
        else:
            ruta = _guardar_archivo(destinatario, asunto, html)
            log.warning("SMTP sin configurar: mail para %s guardado en %s", destinatario, ruta)
    except Exception:
        log.exception("No se pudo enviar el mail a %s (%s)", destinatario, asunto)


def _enviar_smtp(destinatario: str, asunto: str, html: str, texto: str) -> None:
    remitente = settings.SMTP_FROM or settings.SMTP_USER
    msg = EmailMessage()
    msg["Subject"] = asunto
    msg["From"] = formataddr(("ATuCasa", remitente))
    msg["To"] = destinatario
    msg.set_content(texto)
    msg.add_alternative(html, subtype="html")

    contexto = ssl.create_default_context()
    if settings.SMTP_PORT == 465:
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, context=contexto, timeout=20) as s:
            if settings.SMTP_USER:
                s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            s.send_message(msg)
    else:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20) as s:
            s.starttls(context=contexto)
            if settings.SMTP_USER:
                s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            s.send_message(msg)


def _guardar_archivo(destinatario: str, asunto: str, html: str) -> Path:
    carpeta = Path(settings.CORREOS_DIR)
    carpeta.mkdir(parents=True, exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    nombre = re.sub(r"[^a-zA-Z0-9]+", "-", f"{destinatario} {asunto}").strip("-")[:80]
    ruta = carpeta / f"{marca}_{nombre}.html"
    cabecera = f"<!-- Para: {destinatario} | Asunto: {asunto} -->\n"
    ruta.write_text(cabecera + html, encoding="utf-8")
    return ruta
