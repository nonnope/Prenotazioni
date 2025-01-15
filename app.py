# importazione moduli necessari
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import re
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
import os
import uuid
import logging
from datetime import datetime, timedelta, timezone
import threading
import schedule
import time
import csv



# Configurazione logging per il debug
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="app.log",
)

#  Creazione dell'app Flask
app = Flask(__name__)

# Route principale
@app.route("/")
def home():
    return render_template("prenotazioni.html")
    
# gestione errore pagina non trovata
@app.errorhandler(404)
def page_not_found(e):
    return errore_risposta("La pagina richiesta non esiste.", 404)

# directory 
os.makedirs("instance", exist_ok=True)

# configurazione database SQite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prenotazioni.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Modello per la tabella delle prenotazioni
class Prenotazione(db.Model):
    __tablename__ = "prenotazione"
    id = db.Column(db.Integer, primary_key=True)
    codice_prenotazione = db.Column(db.String(50), unique=True, nullable=False)
    ritiro_nome = db.Column(db.String(100), nullable=False)
    ritiro_email = db.Column(db.String(100), nullable=False)
    ritiro_telefono = db.Column(db.String(20), nullable=False)
    citta = db.Column(db.String(50), nullable=False)
    ritiro_indirizzo = db.Column(db.String(200), nullable=False)
    ritiro_dataora = db.Column(db.DateTime, nullable=False)
    consegna_nome = db.Column(db.String(100), nullable=False)
    consegna_email = db.Column(db.String(100), nullable=False)
    consegna_telefono = db.Column(db.String(20), nullable=False)
    consegna_indirizzo = db.Column(db.String(200), nullable=False)
    peso_pacco = db.Column(db.Float, nullable=False)
    stato = db.Column(db.String(20), nullable=False, default='attivo')
    aggiornato = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

# Funzione per la gestione degli errori e invio di risposte in formato JSON
def errore_risposta(message, status_code=400):
    return jsonify({"error": message}), status_code


# Funzione per la convalida dei dati di una prenotazione
def convalida_prenotazione(data, is_new=True):
    # Definizione dei messaggi di errore
    error_messages = {
        "campo_mancante": "Il campo '{field}' è richiesto.",
        "ora_ritiro": "La data di ritiro deve essere almeno un'ora successiva.",
        "ora2_ritiro": "L'orario di ritiro deve essere compreso tra le 8:00 e le 17:00.",
        "peso_non_valido": "Il peso del pacco deve essere positivo.",
        "peso_superato": "il peso massimo consentito è di 100 Kg",
        "telefono_non_valido": "I numeri di telefono devono contenere solo cifre.",
        "formato_non_valido": "Formato della data o del peso non valido.",
        "email_non_valida": "Formato email non valido.",
        "prenotazioni_festive": "Le prenotazioni non possono essere fatte nei giorni festivi.",
        "prenotazioni_domenica": "Le prenotazioni non posso essere fatte di domenica.",
    }
    # campi obbligatori per una prenotazione
    required_fields = [
        "ritiro_nome", "ritiro_email", "ritiro_telefono", "citta",
        "ritiro_indirizzo", "ritiro_dataora", "consegna_nome",
        "consegna_email", "consegna_telefono", "consegna_indirizzo",
        "peso_pacco"
    ]

    # Lista di giorni festivi
    FESTIVI = [
        "2024-01-01", # Capodanno
        "2024-04-25", # Festa della Liberazione
        "2024-05-01", # Festa dei Lavoratori
        "2024-06-02", # Festa della Repubblica
        "2024-12-25", # Natale
        "2024-12-26"  # Santo Stefano
    ]

    # verifica che i campi obbligatori siano preseni
    for field in required_fields:
        if field not in data:
            return error_messages["campo_mancante"].format(field=field), 400

    try:
        ritiro_dataora = datetime.strptime(data["ritiro_dataora"], "%Y-%m-%dT%H:%M")
        #verifica data ritiro
        if ritiro_dataora - datetime.now() < timedelta(hours=1):
            return error_messages["ora_ritiro"], 400
        # Verifica che l'orario sia compreso tra le 8:00 e le 17:00
        if not (8 <= ritiro_dataora.hour < 17 or (ritiro_dataora.hour == 17 and ritiro_dataora.minute == 0)):
            return error_messages["ora2_ritiro"], 400
        #verifica peso del pacco
        if float(data["peso_pacco"]) <= 0:
            return error_messages["peso_non_valido"], 400
        if float(data["peso_pacco"]) > 100:
            return error_messages["peso_superato"], 400
        #verifica numero di telefono
        if not data["ritiro_telefono"].isdigit() or not data["consegna_telefono"].isdigit():
            return error_messages["telefono_non_valido"], 400
        #verifica email con un formato valido
        if not re.match(r"[^@]+@[^@]+\.[^@]+", data["ritiro_email"]):
            return error_messages["email_non_valida"], 400
        # Controllo domenica
        if ritiro_dataora.weekday() == 6:  # Domenica è 6 in Python
            return error_messages["prenotazioni_domenica"], 400
        # Controllo giorni festivi
        if ritiro_dataora.strftime("%Y-%m-%d") in FESTIVI:
            return error_messages["prenotazioni_festive"], 400
    except ValueError:
        return error_messages["formato_non_valido"], 400

    return None

# Generatore di codice prenotazione
def generate_codice_prenotazione(citta):
    codici_citta = {
        "Milano": "MI", "Torino": "TO", "Roma": "RM",
        "Napoli": "NA", "Bologna": "BO", "Firenze": "FI"
    }
    
    codice_citta = codici_citta.get(citta, "XX")
    unique_id = uuid.uuid4().hex[:8].upper()
    return f"{codice_citta}{datetime.now().strftime('%Y%m%d')}-{unique_id}"


# Endpoint per aggiungere una prenotazione
@app.route("/api/prenotazioni", methods=["POST"])
def add_prenotazione():
    data = request.json
    
    # chiamata alla funzione convalida_prenotazione per controllare i dati ricevuti
    error = convalida_prenotazione(data)
    if error:
        return errore_risposta(error[0], error[1]) 
    
    # Conversione della data e ora da stringa a datetime
    ritiro_dataora = datetime.strptime(data["ritiro_dataora"], "%Y-%m-%dT%H:%M")
        
    # generazione del codice di prenotazione
    codice_prenotazione = generate_codice_prenotazione(data["citta"])
    try:
    
    # creazione della prenotazione
        nuova_prenotazione = Prenotazione(
            codice_prenotazione=codice_prenotazione,
            ritiro_nome=data["ritiro_nome"],
            ritiro_email=data["ritiro_email"],
            ritiro_telefono=data["ritiro_telefono"],
            citta=data["citta"],
            ritiro_indirizzo=data["ritiro_indirizzo"],
            ritiro_dataora=ritiro_dataora,
            consegna_nome=data["consegna_nome"],
            consegna_email=data["consegna_email"],
            consegna_telefono=data["consegna_telefono"],
            consegna_indirizzo=data["consegna_indirizzo"],
            peso_pacco=float(data["peso_pacco"]),
            stato="attivo"
        )
   
        db.session.add(nuova_prenotazione)
        db.session.commit()
        logging.info(f"Prenotazione {codice_prenotazione} inserita con successo.")
    except ValueError:
        return errore_risposta("Formato della data di ritiro non valido.", 400)
    except Exception as e:
        db.session.rollback()
        logging.error(f"Errore durante l'aggiunta della prenotazione: {e}")
        return errore_risposta("Errore durante l'aggiunta al database.", 500)


    # invio email
    subject = f"Conferma Prenotazione - Codice: {codice_prenotazione}" 
    body = f"""
    Gentile {data.get("ritiro_nome", "Cliente")},
    
    La tua prenotazione è stata confermata con successo.
    
    **Dettagli Prenotazione**:
    - Codice Prenotazione: {codice_prenotazione}
    - Città: {data.get("citta")}
    - Indirizzo di Ritiro: {data.get("ritiro_indirizzo")}
    - Data e Ora di Ritiro: {data.get("ritiro_dataora")} 
    - Nome referente per la consegna: {data.get("consegna_nome")}
    - Telefono referente: {data.get("consegna_telefono")}
    - Email referente: {data.get("consegna_email")}
    - Indirizzo di Consegna: {data.get("consegna_indirizzo")}
    - Peso del Pacco: {data.get("peso_pacco")} kg
    
    Grazie per aver scelto EcoFriendly Delivery!
    
    Cordiali saluti,  
    Il team EcoFriendly Delivery
    """
    
    try:
        invia_email(data["ritiro_email"], subject, body)
    except Exception as e:
        logging.error(f"Errore durante l'invio dell'email: {e}")
        return errore_risposta("Prenotazione salvata, ma errore nell'invio dell'email.", 500)
    
    
    return jsonify({"message": "Prenotazione aggiunta.", "codice_prenotazione": codice_prenotazione, "nuovo_codice_prenotazione": nuova_prenotazione.id}), 201    

# Endpoint per recuperare i dati di una prenotazione
@app.route("/api/prenotazioni/<codice_prenotazione>", methods=["GET"])
def estrarre_prenotazione(codice_prenotazione):
    prenotazione = Prenotazione.query.filter_by(codice_prenotazione=codice_prenotazione).first()
    if not prenotazione:
        return errore_risposta("Prenotazione non trovata.", 404)

    # Funzione per serializzare i dati
    def elenco_prenotazione(prenotazione):
        return {
            "codice_prenotazione": prenotazione.codice_prenotazione,
            "ritiro_nome": prenotazione.ritiro_nome,
            "ritiro_email": prenotazione.ritiro_email,
            "ritiro_telefono": prenotazione.ritiro_telefono,
            "citta": prenotazione.citta,
            "ritiro_indirizzo": prenotazione.ritiro_indirizzo,
            "ritiro_dataora": prenotazione.ritiro_dataora.strftime("%Y-%m-%dT%H:%M"),
            "consegna_nome": prenotazione.consegna_nome,
            "consegna_email": prenotazione.consegna_email,
            "consegna_telefono": prenotazione.consegna_telefono,
            "consegna_indirizzo": prenotazione.consegna_indirizzo,
            "peso_pacco": prenotazione.peso_pacco
        }

    return jsonify(elenco_prenotazione(prenotazione))

# Endpoint per modificare una prenotazione
@app.route("/api/prenotazioni/<codice_prenotazione>", methods=["PUT"])
def modifica_prenotazione(codice_prenotazione):
    data = request.json
    prenotazione = Prenotazione.query.filter_by(codice_prenotazione=codice_prenotazione, stato="attivo").first()
    if not prenotazione:
        return errore_risposta("Prenotazione non trovata.", 404)
        
    # Validazione dei nuovi dati
    error = convalida_prenotazione(data, is_new=False)
    if error:
        return errore_risposta(error[0], error[1])
    
    try:
        # Conversione della data e ora da stringa a datetime
        ritiro_dataora = datetime.strptime(data["ritiro_dataora"], "%Y-%m-%dT%H:%M")
        
        # Aggiornamento dei dati della prenotazione
        prenotazione.ritiro_nome = data["ritiro_nome"]
        prenotazione.ritiro_email = data["ritiro_email"]
        prenotazione.ritiro_telefono = data["ritiro_telefono"]
        prenotazione.citta = data["citta"]
        prenotazione.ritiro_indirizzo = data["ritiro_indirizzo"]
        prenotazione.ritiro_dataora = ritiro_dataora
        prenotazione.consegna_nome = data["consegna_nome"]
        prenotazione.consegna_email = data["consegna_email"]
        prenotazione.consegna_telefono = data["consegna_telefono"]
        prenotazione.consegna_indirizzo = data["consegna_indirizzo"]
        prenotazione.peso_pacco = float(data["peso_pacco"])
        db.session.commit()
        logging.info(f"Prenotazione {codice_prenotazione} modificata con successo.")
    except Exception as db_error:
        db.session.rollback()
        logging.error(f"Errore durante la modifica della prenotazione: {db_error}")
        return errore_risposta("Errore durante la modifica della prenotazione.", "details:", str(db_error), 500)
    
    # Invia un'email di conferma della modifica
    subject = f"Prenotazione modificata - Codice: {codice_prenotazione}"  # Oggetto con numero prenotazione
    body = f"""
    Gentile {data.get("ritiro_nome", "Cliente")},
    
    La tua prenotazione è stata modificata con successo.
    
    **Dettagli Prenotazione**:
    - Codice Prenotazione: {codice_prenotazione}
    - Città: {data.get("citta")}
    - Indirizzo di Ritiro: {data.get("ritiro_indirizzo")}
    - Data e Ora di Ritiro: {data.get("ritiro_dataora")}
    - Nome referente per la consegna: {data.get("consegna_nome")}
    - Telefono referente: {data.get("consegna_telefono")}
    - Email referente: {data.get("consegna_email")} 
    - Indirizzo di Consegna: {data.get("consegna_indirizzo")}
    - Peso del Pacco: {data.get("peso_pacco")} kg
    
     
    Cordiali saluti,  
    Il team EcoFriendly Delivery
    """
    try:
        invia_email(data["ritiro_email"], subject, body)
    except Exception as email_error:
        logging.error(f"Errore durante l'invio dell'email: {email_error}")
        return errore_risposta("Prenotazione modificata, ma l'invio dell'email non è riuscito.", 500)

    return jsonify({"message": "Prenotazione modificata con successo e email inviata."}), 200

# Endpoint per eliminare una prenotazione
@app.route("/api/prenotazioni/<codice_prenotazione>", methods=["DELETE"])
def cancella_prenotazione(codice_prenotazione):
   # Cerca la prenotazione nel database
    logging.info(f"Richiesta di cancellazione per il codice: {codice_prenotazione}")
   
   # Verifica la prenotazione
    prenotazione = Prenotazione.query.filter_by(codice_prenotazione=codice_prenotazione, stato="attivo").first()
    if not prenotazione:
        logging.warning(f"Nessuna prenotazione trovata per il codice: {codice_prenotazione}")
        return errore_risposta("Prenotazione non trovata.", 404)
   
   # Controlla se la cancellazione è permessa (almeno un'ora prima)
    if prenotazione.ritiro_dataora - datetime.now() < timedelta(hours=1):
        return errore_risposta("Cancellazione permessa almeno un'ora prima.", 400)


    # Recupera i dettagli della prenotazione prima di cancellarla
    recipient_email = prenotazione.ritiro_email
    customer_name = prenotazione.ritiro_nome
    citta = prenotazione.citta
    ritiro_indirizzo = prenotazione.ritiro_indirizzo
    consegna_indirizzo = prenotazione.consegna_indirizzo
    peso_pacco = prenotazione.peso_pacco

    # conrassegna la prenotazione dal database
    try:
        prenotazione.stato = "cancellato"
        db.session.commit()
        logging.info(f"Prenotazione n. {codice_prenotazione} cancellata con successo.")
    except Exception as db_error:
        db.session.rollback()
        logging.error(f"Errore durante la cancellazione della prenotazione: {db_error}")
        return errore_risposta("Errore durante la cancellazione della prenotazione.", "details:", str(db_error),500)

        
    
    # invio email di conferma
    subject = f"Cancellazione Prenotazione - Codice: {codice_prenotazione}"
    body = f"""
    Gentile {customer_name},

    La tua prenotazione con codice **{codice_prenotazione}** è stata cancellata con successo.

    **Dettagli della prenotazione cancellata**:
    - Città: {citta}
    - Indirizzo di Ritiro: {ritiro_indirizzo}
    - Indirizzo di Consegna: {consegna_indirizzo}
    - Peso del Pacco: {peso_pacco} kg
    - Data e Ora di Ritiro: {prenotazione.ritiro_dataora.strftime('%Y-%m-%d alle %H:%M')}

    Ci dispiace vederti andare via, ma speriamo di rivederti presto!

    Cordiali saluti,  
    Il team EcoFriendly Delivery
    """

    # Invia l'email di conferma della cancellazione
    try:
        invia_email(recipient_email, subject, body)
    except Exception as e:
        logging.error(f"Errore durante l'invio dell'email: {e}")
        return errore_risposta("Prenotazione cancellata, ma l'invio dell'email non è riuscito.", 500)

    return jsonify({"message": "Prenotazione cancellata con successo e email inviata."}), 200


# tabella per tener traccia dell'ultimo invio per ogni città
class SyncLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    citta = db.Column(db.String(50), unique=True, nullable=False)
    ultima_sincro = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))


# Dizionario per le email specifiche per città
EMAIL_CITTA = {
    "Milano": [ milano_ufficio1@example.com", "milano_ufficio2@example.com"],
    "Roma": ["roma_ufficio1@example.com", "roma_ufficio2@example.com"],
    "Torino": ["torino_ufficio1@example.com", "torino_ufficio2@example.com"],
    "Napoli": ["napoli@example.com", "napoli_ufficio_2@example.com"],
    "Bologna": ["bologna@example.com", "bologna_ufficio2@example.com"],
    "Firenze": ["firenze@example.com", "firenze_ufficio2@example.com"]
    }
# Funzione per ottenere l'ultimo timestamp
def ultima_sincro(citta):
    log = SyncLog.query.filter_by(citta=citta).first()
    if not log:
        # Se non esiste un record, crea uno con timestamp iniziale
        log = SyncLog(citta=citta, ultima_sincro=datetime.min.replace(tzinfo=timezone.utc))
        db.session.add(log)
        db.session.commit()
    return log.ultima_sincro or datetime.min.replace(tzinfo=timezone.utc)

# funzione per l'esportazione dei dati
def export_dati(citta, all_data=True, ultima_sincro=None):
    if not all_data and not isinstance(ultima_sincro, datetime):
        ultima_sincro = datetime.min

    if all_data:
        prenotazioni = Prenotazione.query.filter_by(citta=citta).all()
    else:
        prenotazioni = Prenotazione.query.filter(Prenotazione.citta == citta, Prenotazione.aggiornato > ultima_sincro).all()

    nome_file = os.path.join("instance", f"prenotazioni_{'complete' if all_data else 'incrementali'}_{citta}.csv")
    with open(nome_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["codice_prenotazione", "ritiro_nome", "ritiro_email", "ritiro_telefono","citta", "ritiro_indirizzo", "ritiro_dataora", "consegna_nome", "consegna_email", "consegna_telefono", "consegna_indirizzo", "peso_pacco", "stato", "aggiornato"])
        for prenotazione in prenotazioni:
            writer.writerow([prenotazione.codice_prenotazione, prenotazione.ritiro_nome, prenotazione.ritiro_email, prenotazione.ritiro_telefono, prenotazione.citta, prenotazione.ritiro_indirizzo, prenotazione.ritiro_dataora.strftime("%Y-%m-%dT%H:%M"), prenotazione.consegna_nome, prenotazione.consegna_email, prenotazione.consegna_telefono, prenotazione.consegna_indirizzo, prenotazione.peso_pacco, prenotazione.stato, prenotazione.aggiornato])
    logging.info(f"File CSV generato: {nome_file}")
    return nome_file
    
# Funzione per aggiornare l'ultimo timestamp di sincronizzazione
def aggiorna_ultima_sincro(citta):
    log = SyncLog.query.filter_by(citta=citta).first()
    if log:
        log.ultima_sincro = datetime.now(timezone.utc)  # Aggiorna il timestamp con l'ora corrente
        db.session.commit()
    else:
        # Se il record non esiste, creane uno nuovo
        log = SyncLog(citta=citta, ultima_sincro=datetime.now(timezone.utc))
        db.session.add(log)
        db.session.commit()


# task per inviare i dati ogni ora
def invio_export_ora():
    for citta, emails in EMAIL_CITTA.items():
        ultima_sync = ultima_sincro(citta)
        nome_file = export_dati(citta, all_data=False, ultima_sincro=ultima_sincro)  # Esporta dati incrementali
        invia_email(
            to_email=", ".join(emails),
            subject=f"Prenotazioni incrementali - {citta}",
            body=f"Allegato il file delle prenotazioni incrementali per la città di {citta}.",
            attachment_path=nome_file
        )
        aggiorna_ultima_sincro(citta)  # Aggiorna l'ultimo timestamp
    logging.info("Invio incrementale completato.")



# Task per inviare i dati completi ogni sera
def invio_export_giorno():
    for citta, emails in EMAIL_CITTA.items():
        nome_file = export_dati(citta, all_data=True)  # Esporta tutti i dati
        invia_email(
            to_email=", ".join(emails),
            subject=f"Prenotazioni complete - {citta}",
            body=f"Allegato il file delle prenotazioni aggiornate per la città di {citta}.",
            attachment_path=nome_file
        )
    logging.info("Esportazione giornaliera completata.")


# Pianifica il task alle 22:00
schedule.every().day.at("22:00").do(invio_export_giorno)

# Pianifica l'invio incrementale ogni ora dalle 8:01 alle 17:01
for hour in range(8, 18):  # Da 8:01 a 17:01
    time_str = f"{hour:02d}:01"
    #logging.info(f"Pianificazione per le {time_str}")
    schedule.every().day.at(time_str).do(invio_export_ora)


# funzione per eseguire schedule su un thread separato
def schedule_runner():
    logging.info("Avviando il runner dello scheduler...")
    while True:
        schedule.run_pending()
        time.sleep(300)  # Controlla i task ogni 60 secondi
    

# Funzione per inviare email

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# Leggi le credenziali SMTP dal file .env
username = os.getenv("SMTP_USERNAME")
password = os.getenv("SMTP_PASSWORD")
smtp_server = os.getenv("SMTP_SERVER")
smtp_port = int(os.getenv("SMTP_PORT"))



def invia_email(to_email, subject, body, attachment_path=None):
    logging.info(f"Invio email a: {to_email}, Allegato: {attachment_path}")
    try:
        # Creazione del messaggio email
        msg = MIMEMultipart() if attachment_path else MIMEText(body, "plain", "utf-8")
        
        if attachment_path:
            # Se c'è un allegato, usa MIMEMultipart
            msg = MIMEMultipart()
            msg.attach(MIMEText(body, "plain"))
            # Aggiungi l'allegato
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}")
            msg.attach(part)
        else:
            # Solo testo se non c'è allegato
            msg = MIMEText(body, "plain", "utf-8")
        
        # Configurazione dell'email
        msg["Subject"] = subject
        msg["From"] = username
        msg["To"] = to_email
        
        # Creazione di un contesto SSL
        context = ssl.create_default_context()
        
        # Connessione al server smtp
        with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=10) as server:
            server.login(username, password)
            server.sendmail(username, to_email, msg.as_string())
            logging.info(f"Email inviata con successo a {to_email}")
    except Exception as e:
        logging.error(f"Errore durante l'invio dell'email: {e}")
        return errore_risposta("Errore durante l'invio dell'email.", 500)

if __name__ == "__main__":
    with app.app_context():
        
        schedule.every().day.at("22:00").do(invio_export_giorno)
        logging.info("Task giornaliero pianificato per le 22:00.")

              
        # Pianifica l'invio incrementale ogni ora tra le 8:01 e le 17:01
        for hour in range(8, 18):
            time_str = f"{hour:02d}:01"
            schedule.every().day.at(time_str).do(invio_export_ora)
            logging.info(f"Task incrementale pianificato per {time_str}.")
        
        # Forza l'esecuzione immediata di tutti i task per il test
        #schedule.run_all(delay_seconds=300)

    # Avvia il thread per la pianificazione
    schedule_thread = threading.Thread(target=schedule_runner)
    schedule_thread.daemon = True  # Permette di chiudere il thread quando l'app principale termina
    schedule_thread.start()
    logging.info("Thread dello scheduler avviato.")

        
    # Avvia l'app Flask
    app.run(host="0.0.0.0", port=5000, debug=True)
