# config.py
import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env
load_dotenv()


# Configurazione di base dell'applicazione.
class Config:
    
    # Configurazione del database
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'database', 'prenotazioni.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configurazione per l'invio delle email
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = int(os.getenv("SMTP_PORT"))
    EMAIL_ALIAS = os.getenv("EMAIL_ALIAS", None)

    # Configurazioni generali
    DEBUG = os.getenv("DEBUG", "True") == "True"
