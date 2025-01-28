from flask import Blueprint, render_template, request, jsonify
from datetime import date, datetime, timedelta
import logging
from models import Prenotazione, db
from utils.validation import convalida_prenotazione
from utils.email_utils import invia_email
import uuid

# Creazione del blueprint
prenotazioni_bp = Blueprint('prenotazioni', __name__)

# Route per servire il frontend
@prenotazioni_bp.route("/", methods=["GET"])
def home():
    return render_template("prenotazioni.html")

# Funzione di errore standard
def errore_risposta(message, status_code=400):
    return jsonify({"error": message}), status_code

# funzione per generare il codice prenotazione
def generate_codice_prenotazione(citta):
    codici_citta = {
        "Milano": "MI", "Torino": "TO", "Roma": "RM",
        "Napoli": "NA", "Bologna": "BO", "Firenze": "FI"
    }

    codice_citta = codici_citta.get(citta, "XX")
    unique_id = uuid.uuid4().hex[:8].upper()
    return f"{codice_citta}{datetime.now().strftime('%Y%m%d')}-{unique_id}"



# Endpoint per aggiungere una prenotazione
@prenotazioni_bp.route("/", methods=["POST"])
def add_prenotazione():
    # Convalida i dati
    data = request.json
    error = convalida_prenotazione(data)
    if error:
        return errore_risposta(error[0], error[1])

    ritiro_dataora = datetime.strptime(data["ritiro_dataora"], "%Y-%m-%dT%H:%M")
    codice_prenotazione = generate_codice_prenotazione(data["citta"])
    try:
        # Crea un nuovo oggetto Prenotazione
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

        # Aggiunge la prenotazione al database
        db.session.add(nuova_prenotazione)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"Errore durante l'aggiunta della prenotazione: {e}")
        return errore_risposta("Errore durante l'aggiunta al database.", 500)

       
    # invio email di conferma
    subject = f"Conferma Prenotazione - Codice: {codice_prenotazione}" 
    body = f"""
    Gentile {data.get("ritiro_nome", "Cliente")},
    
    La sua prenotazione è stata confermata con successo.
    
    Dettagli Prenotazione:

    - Codice Prenotazione: {codice_prenotazione}
    - Città: {data.get("citta")}
    - Indirizzo di Ritiro: {data.get("ritiro_indirizzo")}
    - Data e Ora di Ritiro: {ritiro_dataora.strftime('%d-%m-%Y alle %H:%M')} 
    - Nome referente per la consegna: {data.get("consegna_nome")}
    - Telefono referente: {data.get("consegna_telefono")}
    - Email referente: {data.get("consegna_email")}
    - Indirizzo di Consegna: {data.get("consegna_indirizzo")}
    - Peso del Pacco: {data.get("peso_pacco")} kg
    
    Grazie per aver scelto Eco Friendly Delivery!
    
    Cordiali saluti,  
    Il team Eco Friendly Delivery
    """
    
    try:
        invia_email(data["ritiro_email"], subject, body)
    except Exception as e:
        logging.error(f"Errore durante l'invio dell'email: {e}")
        return errore_risposta("Prenotazione salvata, ma errore nell'invio dell'email.", 500)
    
    
    return jsonify({"message": "Prenotazione aggiunta.", "codice_prenotazione": codice_prenotazione, "nuovo_codice_prenotazione": nuova_prenotazione.id}), 201    


# Endpoint per recuperare i dati di una prenotazione tramite il codice prenotazione
@prenotazioni_bp.route("/<codice_prenotazione>", methods=["GET"])
def estrarre_prenotazione(codice_prenotazione):
    prenotazione = Prenotazione.query.filter_by(codice_prenotazione=codice_prenotazione).first()
    if not prenotazione:
        return errore_risposta("Prenotazione non trovata.", 404)

    return jsonify({
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
    })

# Endpoint per modificare una prenotazione esistente
@prenotazioni_bp.route("/<codice_prenotazione>", methods=["PUT"])
def modifica_prenotazione(codice_prenotazione):
    # Recupera i dati della richiesta JSON
    data = request.json
    
    # Cerca la prenotazione nel database in base al codice prenotazione e stato "attivo"
    prenotazione = Prenotazione.query.filter_by(codice_prenotazione=codice_prenotazione, stato="attivo").first()
    if not prenotazione:
        return errore_risposta("Prenotazione non trovata.", 404)
    
    # Controlla se la data di ritiro della prenotazione è scaduta
    if prenotazione.ritiro_dataora < datetime.now():
        logging.warning(f"Tentativo di modifica di una prenotazione scaduta: {codice_prenotazione}")
        return errore_risposta("Impossibile modificare una prenotazione già scaduta.", 400)
    
    # Convalida i dati della prenotazione
    error = convalida_prenotazione(data, is_new=False)
    if error:
        return errore_risposta(error[0], error[1])

    try:
        # Converte la data e ora di ritiro dalla stringa in un oggetto datetime
        ritiro_dataora = datetime.strptime(data["ritiro_dataora"], "%Y-%m-%dT%H:%M")
        
        # Aggiorna i campi della prenotazione con i nuovi dati
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
        
        # Salva le modifiche nel database
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"Errore durante la modifica della prenotazione: {e}")
        return errore_risposta("Errore durante la modifica della prenotazione.", 500)

       
    # Invia un'email di conferma della modifica
    subject = f"Prenotazione modificata - Codice: {codice_prenotazione}"  # Oggetto con numero prenotazione
    body = f"""
    Gentile {data.get("ritiro_nome", "Cliente")},
    
    La sua prenotazione è stata modificata con successo.
    
    Dettagli Prenotazione:

    - Codice Prenotazione: {codice_prenotazione}
    - Città: {prenotazione.citta}
    - Indirizzo di Ritiro: {prenotazione.ritiro_indirizzo}
    - Data e Ora di Ritiro: {prenotazione.ritiro_dataora.strftime('%d-%m-%Y alle %H:%M')}
    - Nome referente per la consegna: {prenotazione.consegna_nome}
    - Telefono referente: {prenotazione.consegna_telefono}
    - Email referente: {prenotazione.consegna_email}
    - Indirizzo di Consegna: {prenotazione.consegna_indirizzo}
    - Peso del Pacco: {prenotazione.peso_pacco} kg
     
    Cordiali saluti,  
    Il team Eco Friendly Delivery
    """
    try:
        invia_email(data["ritiro_email"], subject, body)
    except Exception as email_error:
        logging.error(f"Errore durante l'invio dell'email: {email_error}")
        return errore_risposta("Prenotazione modificata, ma l'invio dell'email non è riuscito.", 500)

    return jsonify({"message": "Prenotazione modificata con successo e email inviata."}), 200



# Endpoint per eliminare una prenotazione
@prenotazioni_bp.route("/<codice_prenotazione>", methods=["DELETE"])
def cancella_prenotazione(codice_prenotazione):
    # Cerca la prenotazione nel database in base al codice e stato "attivo"
    prenotazione = Prenotazione.query.filter_by(codice_prenotazione=codice_prenotazione, stato="attivo").first()
    if not prenotazione:
        return errore_risposta("Prenotazione non trovata.", 404)
    
    # Controlla se la data di ritiro della prenotazione è scaduta
    if prenotazione.ritiro_dataora < datetime.now():
        logging.warning(f"Tentativo di cancellazione di una prenotazione scaduta: {codice_prenotazione}")
        return errore_risposta("Impossibile cancellare una prenotazione già scaduta.", 400)

    # Aggiorna lo stato della prenotazione a "cancellato"
    try:
        prenotazione.stato = "cancellato"
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"Errore durante la cancellazione della prenotazione: {e}")
        return errore_risposta("Errore durante la cancellazione della prenotazione.", 500)

    # invio email di conferma della cancellazione
    subject = f"Cancellazione Prenotazione - Codice: {codice_prenotazione}"
    body = f"""
    Gentile {prenotazione.ritiro_nome if prenotazione.ritiro_nome else "Cliente"},

    La sua prenotazione con codice **{codice_prenotazione}** è stata cancellata con successo.

    Dettagli della prenotazione cancellata:

    - Codice Prenotazione: {codice_prenotazione}
    - Città: {prenotazione.citta}
    - Indirizzo di Ritiro: {prenotazione.ritiro_indirizzo}
    - Nome referente per la consegna: {prenotazione.consegna_nome}
    - Telefono referente: {prenotazione.consegna_telefono}
    - Email referente: {prenotazione.consegna_email} 
    - Indirizzo di Consegna: {prenotazione.consegna_indirizzo}
    - Peso del Pacco: {prenotazione.peso_pacco} kg
    - Data e Ora di Ritiro: {prenotazione.ritiro_dataora.strftime('%Y-%m-%d alle %H:%M')}

    Ci dispiace vederti andare via, ma speriamo di rivederti presto!

    Cordiali saluti,  
    Il team Eco Friendly Delivery
    """

    try:
        invia_email(prenotazione.ritiro_email, subject, body)
    except Exception as e:
        logging.error(f"Errore durante l'invio dell'email: {e}")
        return errore_risposta("Prenotazione cancellata, ma l'invio dell'email non è riuscito.", 500)

    return jsonify({"message": "Prenotazione cancellata con successo e email inviata."}), 200
