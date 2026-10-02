"""Envía 2026-09/index.html tal cual (sin sanitizar) a una casilla de prueba vía SMTP de Gmail.

Uso: python3 enviar-prueba.py [destinatario] [remitente]
La cuenta UChile tiene bloqueadas las contraseñas de aplicación; usar una cuenta Gmail personal como remitente.
Pide una contraseña de aplicación de Google (myaccount.google.com/apppasswords); no se guarda.
"""
import getpass, smtplib, sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

destino = sys.argv[1] if len(sys.argv) > 1 else "cmartinezg@uchile.cl"
remitente = sys.argv[2] if len(sys.argv) > 2 else "chuchurex@gmail.com"
html = (Path(__file__).parent / "2026-09" / "index.html").read_text(encoding="utf-8")

msg = MIMEMultipart("alternative")
msg["Subject"] = "[Propuesta responsive] Diario Mural Universitario - La Uchile en septiembre"
msg["From"] = remitente
msg["To"] = destino
msg.attach(MIMEText("Versión HTML del Diario Mural Universitario.", "plain", "utf-8"))
msg.attach(MIMEText(html, "html", "utf-8"))

clave = getpass.getpass(f"Contraseña de aplicación para {remitente}: ").replace(" ", "")
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
    s.login(remitente, clave)
    s.send_message(msg)
print(f"Enviado a {destino}")
