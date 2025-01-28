# Progetto Prenotazioni

# Obiettivi del Progetto

L'obiettivo principale del progetto Prenotazioni è fornire un sistema per gestire le prenotazioni.

Il sistema permette di:

- Gestire e organizzare le prenotazioni da parte degli utenti.
- Notificare gli utenti tramite email per conferme o modifiche.

Questo progetto è organizzato in due sezioni principali: Backend e Frontend.

# Struttura del Progetto

backend/
├── database/
│ └── prenotazioni.db
├── routes/
│ ├── **init**.py
│ ├── error_handlers.py
│ └── prenotazioni.py
├── utils/
│ ├── email_utils.py
│ ├── scheduling.py
│ └── validation.py
├── app.log
├── app.py
├── config.py
├── models.py
└── requirements.txt

frontend/
├── static/
│ ├── favicon.png
│ ├── scripts.js
│ ├── sfondo.webp
│ └── styles.css
├── templates/
│ └── prenotazioni.html

.env
.gitignore
README.md

# Backend

Il backend è costruito con Flask e include tutte le logiche di business, le API e la gestione dei dati.

Setup Backend

1. Assicurati di avere Python installato.

2. Crea un ambiente virtuale:

python -m venv .venv
.venv/bin/activate # Su Windows: .venv\Scripts\activate

3. Installare il framework falsk

pip install flask

4. Installa le dipendenze:

pip install -r backend/requirements.txt

5. Configura il file .env per le variabili di ambiente.

6. Genera il database (solo la prima volta):

Per creare il database prenotazioni.db:

- crea la cartella database nel backend
- modifica il file app.py come segue:

if __name__ == "__main__":
   with app.app_context():
      db.create_all() # Crea il database e le tabelle
   app.run(host="0.0.0.0", port=5000, debug=False)

7. Avvia il server:

python backend/app.py

8. Accedi al server tramite http://127.0.0.1:5000.

# Struttura Backend

- database/: Contiene il file prenotazioni.db dove vengono gestiti i dati delle prenotazioni

- routes/: Contiene i file che definiscono le route e gli endpoint.

- utils/: Funzioni di utilità come gestione email, validazioni, e scheduler.

- app.py: Punto di ingresso principale dell'applicazione.

- config.py: Configurazioni globali dell'applicazione.

- models.py: Modelli e gestione dei dati.

# Frontend

Il frontend contiene tutti i file statici e i template HTML per la presentazione all'utente.

Struttura Frontend

- static/: File CSS, JavaScript, immagini e risorse statiche.

- templates/: Template HTML utilizzati dal backend per il rendering delle pagine dinamiche.

# Configurazione Frontend

Il backend serve direttamente i file statici e i template del frontend.
Non è necessaria una configurazione separata per il frontend.

# File .env

Il file .env contiene le variabili di configurazione sensibili come:

SMTP_USERNAME=tua_username
SMTP_PASSWORD=tua_password
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
EMAIL_ALIAS=example@example.com


# File .gitignore

Il file .gitignore impedisce di includere file sensibili o non necessari nel repository Git.
Alcune voci incluse:

Python
**pycache**/
_.pyc
_.pyo
instance/

Logs
\*.log

Ambiente virtuale
.venv/
env/
\*.env

