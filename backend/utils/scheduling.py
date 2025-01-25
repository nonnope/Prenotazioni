import os
import logging
import schedule
import time
import csv
from datetime import datetime, timezone
from models import Prenotazione, SyncLog, db
from utils.email_utils import invia_email
from flask import current_app as app

# email specifiche per città
EMAIL_CITTA = {
    "Milano": ["milano_ufficio1@example.com","milano_ufficio2@example.com"],
    "Roma": ["roma_ufficio1@example.com","roma_ufficio2@example.com"],
    "Torino": ["torino_ufficio1@example.com", "torin cio2@example.com"],
    "Napoli": ["napoli@example.com", "napoli_ufficio_2@example.com"],
    "Bologna": ["bologna@example.com", "bologna_ufficio2@example.com"],
    "Firenze": ["firenze@example.com", "firenze_ufficio2@example.com"]
}

# Funzione per ottenere l'ultimo timestamp di sincronizzazione per una città
def ultima_sincro(citta):
    with app.app_context():
        log = SyncLog.query.filter_by(citta=citta).first()
        if not log:
            # Crea un nuovo record di sincronizzazione se non esiste
            log = SyncLog(citta=citta, ultima_sincro=datetime.min.replace(tzinfo=timezone.utc))
            db.session.add(log)
            db.session.commit()
        return log.ultima_sincro or datetime.min.replace(tzinfo=timezone.utc)

# Funzione per esportare i dati delle prenotazioni
def export_dati(citta, all_data=True, ultima_sincro=None):
    if not all_data and not isinstance(ultima_sincro, datetime):
        ultima_sincro = datetime.min.replace(tzinfo=timezone.utc)

    # Query per recuperare le prenotazioni
    if all_data:
        prenotazioni = Prenotazione.query.filter_by(citta=citta).all()
    else:
        prenotazioni = Prenotazione.query.filter(
            Prenotazione.citta == citta,
            Prenotazione.aggiornato > ultima_sincro
        ).all()
    
    # Percorso completo del file CSV
    database_path = os.path.join(os.path.dirname(__file__), '..', 'database')
        
    nome_file = os.path.join(database_path, f"prenotazioni_{'complete' if all_data else 'incrementali'}_{citta}.csv")
    
    # Genera il file CSV
    with open(nome_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "codice_prenotazione", "ritiro_nome", "ritiro_email", "ritiro_telefono",
            "citta", "ritiro_indirizzo", "ritiro_dataora", "consegna_nome", 
            "consegna_email", "consegna_telefono", "consegna_indirizzo", 
            "peso_pacco", "stato", "aggiornato"
        ])
        for prenotazione in prenotazioni:
            writer.writerow([
                prenotazione.codice_prenotazione, prenotazione.ritiro_nome, prenotazione.ritiro_email,
                prenotazione.ritiro_telefono, prenotazione.citta, prenotazione.ritiro_indirizzo,
                prenotazione.ritiro_dataora.strftime("%Y-%m-%dT%H:%M"), prenotazione.consegna_nome,
                prenotazione.consegna_email, prenotazione.consegna_telefono, prenotazione.consegna_indirizzo,
                prenotazione.peso_pacco, prenotazione.stato, prenotazione.aggiornato
            ])
    logging.info(f"File CSV generato: {nome_file}")
    return nome_file

# Funzione per aggiornare l'ultimo timestamp di sincronizzazione
def aggiorna_ultima_sincro(citta):
    with app.app_context():
        # Cerca un record di sincronizzazione per la città
        log = SyncLog.query.filter_by(citta=citta).first()
        
        if log:
            # Se il record esiste, aggiorna il timestamp
            log.ultima_sincro = datetime.now(timezone.utc)
            db.session.commit()
        else:
            # Se il record non esiste, creane uno nuovo
            log = SyncLog(citta=citta, ultima_sincro=datetime.now(timezone.utc))
            db.session.add(log)
            db.session.commit()

# Task per esportare e inviare i dati incrementali ogni ora
def invio_export_ora():
    with app.app_context():
        # Itera su ciascuna città e i rispettivi destinatari email
        for citta, emails in EMAIL_CITTA.items():
            ultima_sync = ultima_sincro(citta)
            
            # Esporta i dati incrementali in un file CSV
            nome_file = export_dati(citta, all_data=False, ultima_sincro=ultima_sync)
            
            # Invia l'email con il file CSV allegato
            invia_email(
                to_email=emails,  
                subject=f"Prenotazioni incrementali - {citta}",
                body=f"Allegato il file delle prenotazioni incrementali per la città di {citta}.",
                attachment_path=nome_file
            )

            # Aggiorna il timestamp dell'ultima sincronizzazione per la città
            aggiorna_ultima_sincro(citta)
        logging.info("Invio incrementale completato.")

# Task per inviare i dati completi ogni sera
def invio_export_giorno():
    with app.app_context():
         # Itera su ciascuna città e i rispettivi destinatari email
        for citta, emails in EMAIL_CITTA.items():

            # Esporta tutti i dati in un file CSV
            nome_file = export_dati(citta, all_data=True)

            # Invia l'email con il file CSV allegato
            invia_email(
                to_email=emails, 
                subject=f"Prenotazioni complete - {citta}",
                body=f"Allegato il file delle prenotazioni aggiornate per la città di {citta}.",
                attachment_path=nome_file
            )
        logging.info("Invio giornaliero completato.")

# Pianificazione dei task
# Esporta i dati incrementali in un file CSV
schedule.every().day.at("22:00").do(invio_export_giorno)

# Pianifica i task orari tra le 8:01 e le 17:01
for hour in range(8, 18):  
    time_str = f"{hour:02d}:01"
    schedule.every().day.at(time_str).do(invio_export_ora)

# Funzione per eseguire schedule su un thread separato
def schedule_runner(app):
    logging.info("Avviando il runner dello scheduler...")
    with app.app_context():
        while True:
            schedule.run_pending()
            time.sleep(300)
        
