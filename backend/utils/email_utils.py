import os
import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from config import Config

# Funzione per inviare email
def invia_email(to_email, subject, body, attachment_path=None):
   
    # Invia un'email utilizzando le configurazioni SMTP definite nel file di configurazione.
    
    logging.info(f"Invio email a: {to_email}, Allegato: {attachment_path}")
    try:
        # Recupera le credenziali e le configurazioni dal file di configurazione
        username = Config.SMTP_USERNAME
        password = Config.SMTP_PASSWORD
        smtp_server = Config.SMTP_SERVER
        smtp_port = Config.SMTP_PORT
        alias = Config.EMAIL_ALIAS

        # Crea il messaggio email
        if attachment_path:
            # Se è presente un allegato, crea un messaggio multipart
            msg = MIMEMultipart()
            msg.attach(MIMEText(body, "plain"))

            # Aggiungi l'allegato
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(attachment_path)}"
                )
                msg.attach(part)
        else:
            # Crea un messaggio semplice senza allegato
            msg = MIMEText(body, "plain", "utf-8")

        # Configura i dettagli dell'email (mittente, destinatario, oggetto)
        msg["From"] = f"{alias} <{username}>" if alias else username
        msg["To"] = ", ".join(to_email) if isinstance(to_email, list) else to_email  # Converte in stringa solo se è una lista #to_email
        msg["Subject"] = subject

        # Crea una connessione sicura SSL al server SMTP
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(username, password)
            server.sendmail(username, to_email, msg.as_string())
            logging.info(f"Email inviata con successo a {to_email}")

    except Exception as e:
        logging.error(f"Errore durante l'invio dell'email: {e}")
        raise Exception("Errore durante l'invio dell'email.")
