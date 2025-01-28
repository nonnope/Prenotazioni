# app.py
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from routes import register_blueprints
from config import Config
import threading
import logging
import os
from utils.scheduling import schedule_runner
from models import db

# Configurazione iniziale dell'app Flask
app = Flask(__name__, static_folder="../frontend/static", template_folder="../frontend/templates")
app.config.from_object(Config)

# configurazione del database
db.init_app(app)

# Registrazione dei blueprint per modularizzare le rotte
register_blueprints(app)

# Rotta principale per la homepage
@app.route("/")
def home():
    return render_template("prenotazioni.html")


# Definizione del percorso per il file di log
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.log")

# Creazione del file di log se non esiste
if not os.path.exists(log_dir):
    open(log_dir, 'w').close()  # Crea un file vuoto

# Configurazione del logging
logging.basicConfig(
    filename=log_dir,  
    level=logging.DEBUG,  
    format='%(asctime)s - %(levelname)s - %(message)s',  
    filemode='a'  
)


# Avvia un thread separato per eseguire task pianificati in background
logging.info("Avvio del thread per i task pianificati.")
schedule_thread = threading.Thread(target=schedule_runner, args=(app,))
schedule_thread.daemon = True
schedule_thread.start()
logging.info("Therad avviato con successo")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
