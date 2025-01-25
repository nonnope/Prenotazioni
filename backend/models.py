# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class Prenotazione(db.Model):
    __tablename__ = "prenotazione"
    
    # Definisce il modello per una prenotazione di spedizione
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

class SyncLog(db.Model):
    __tablename__ = "sync_log"

    id = db.Column(db.Integer, primary_key=True)
    citta = db.Column(db.String(50), unique=True, nullable=False)
    ultima_sincro = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
