from flask import Blueprint, jsonify

# Creazione del blueprint per la gestione degli errori
error_handlers_bp = Blueprint('error_handlers', __name__)

# Gestione errore 404 (pagina non trovata)
@error_handlers_bp.app_errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "La pagina richiesta non esiste."}), 404

# Gestione errore 500 (errore interno del server)
@error_handlers_bp.app_errorhandler(500)
def internal_server_error(e):
    return jsonify({"error": "Errore interno del server. Riprova più tardi."}), 500

# Gestione errore generico (default)
@error_handlers_bp.app_errorhandler(Exception)
def generic_error(e):
    return jsonify({"error": "Si è verificato un errore imprevisto."}), 500
