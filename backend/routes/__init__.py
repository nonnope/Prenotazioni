from flask import Flask
from .prenotazioni import prenotazioni_bp
from .error_handlers import error_handlers_bp

def register_blueprints(app: Flask):
    
    # Blueprint per la gestione delle prenotazioni
    app.register_blueprint(prenotazioni_bp, url_prefix='/api/prenotazioni')
    
    # Blueprint per la gestione degli errori
    app.register_blueprint(error_handlers_bp)
