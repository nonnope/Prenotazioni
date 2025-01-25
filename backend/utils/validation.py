from datetime import datetime, timedelta
import re



# Funzione per la convalida dei dati di una prenotazione
def convalida_prenotazione(data, is_new=True):
    # Definizione dei messaggi di errore
    error_messages = {
        "campo_mancante": "Il campo '{field}' è richiesto.",
        "ora_ritiro": "La data di ritiro deve essere almeno due ore successiva.",
        "ora2_ritiro": "L'orario di ritiro deve essere compreso tra le 8:00 e le 17:00.",
        "ora3_ritiro": "L'orario di ritiro deve essere a mezz'ora esatta (es. 8:00, 8:30).",
        "peso_non_valido": "Il peso del pacco deve essere positivo.",
        "peso_superato": "Il peso massimo consentito è di 100 Kg.",
        "telefono_non_valido": "I numeri di telefono devono contenere solo cifre.",
        "formato_non_valido": "Formato della data o del peso non valido.",
        "email_non_valida": "Formato email non valido.",
        "prenotazioni_festive": "Le prenotazioni non possono essere fatte nei giorni festivi.",
        "prenotazioni_domenica": "Le prenotazioni non possono essere fatte di domenica.",
    }

    # Campi obbligatori per una prenotazione
    required_fields = [
        "ritiro_nome", "ritiro_email", "ritiro_telefono", "citta",
        "ritiro_indirizzo", "ritiro_dataora", "consegna_nome",
        "consegna_email", "consegna_telefono", "consegna_indirizzo",
        "peso_pacco"
    ]

    # Lista di giorni festivi
    FESTIVI = [
        "2025-01-01",  # Capodanno
        "2025-04-25",  # Festa della Liberazione
        "2025-05-01",  # Festa dei Lavoratori
        "2025-06-02",  # Festa della Repubblica
        "2025-12-25",  # Natale
        "2025-12-26"   # Santo Stefano
    ]

    # Verifica che i campi obbligatori siano presenti
    for field in required_fields:
        if field not in data:
            return error_messages["campo_mancante"].format(field=field), 400

    try:
        # Conversione della data e ora
        ritiro_dataora = datetime.strptime(data["ritiro_dataora"], "%Y-%m-%dT%H:%M")

        # Verifica che la data di ritiro sia almeno 3 ore successiva
        if ritiro_dataora - datetime.now() < timedelta(hours=2):
            return error_messages["ora_ritiro"], 400

        # Verifica Orario di lavoro e mezz'ora precisa
        if not (8 <= ritiro_dataora.hour < 17 or (ritiro_dataora.hour == 17 and ritiro_dataora.minute == 0)):
            return error_messages["ora2_ritiro"], 400
        if ritiro_dataora.minute not in [0, 30]:
            return error_messages ["ora3_ritiro"], 400

        # Verifica peso del pacco
        if float(data["peso_pacco"]) <= 0:
            return error_messages["peso_non_valido"], 400
        if float(data["peso_pacco"]) > 100:
            return error_messages["peso_superato"], 400

        # Verifica numeri di telefono
        if not data["ritiro_telefono"].isdigit() or not data["consegna_telefono"].isdigit():
            return error_messages["telefono_non_valido"], 400

        # Verifica email con un formato valido
        if not re.match(r"[^@]+@[^@]+\.[^@]+", data["ritiro_email"]):
            return error_messages["email_non_valida"], 400

        # Verifica domenica e giorni festivi
        if ritiro_dataora.weekday() == 6:  
            return error_messages["prenotazioni_domenica"], 400
        if ritiro_dataora.strftime("%Y-%m-%d") in FESTIVI:
            return error_messages["prenotazioni_festive"], 400

    except ValueError:
        return error_messages["formato_non_valido"], 400

    return None

