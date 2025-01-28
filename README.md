# Progetto Prenotazioni

# Obiettivi del Progetto

L'obiettivo principale del progetto Prenotazioni è fornire un sistema intuitivo e scalabile per gestire le prenotazioni di risorse o eventi.

Il sistema permette di:

- Gestire e organizzare le prenotazioni da parte degli utenti.
- Notificare gli utenti tramite email per conferme o modifiche.

Questo progetto è organizzato in due sezioni principali: Backend e Frontend, con l'obiettivo di separare la logica server dalla presentazione utente.

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
source .venv/bin/activate # Su Windows: .venv\Scripts\activate

3. Installa le dipendenze:

pip install -r backend/requirements.txt

4. Configura il file .env per le variabili di ambiente (es. credenziali,
   configurazioni).

5. Genera il database (solo la prima volta):

Per creare il database prenotazioni.db, modifica il file app.py come segue:

if **name** == "**main**":
   with app.app_context():
      db.create_all() # Crea il database e le tabelle
   app.run(host="0.0.0.0", port=5000, debug=False)

6. Avvia il server:

python backend/app.py

7. Accedi al server tramite http://127.0.0.1:5000.

# Struttura Backend

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

Nota: Non condividere il file .env su GitHub o altre piattaforme pubbliche.

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

