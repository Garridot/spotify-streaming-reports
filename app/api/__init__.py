from .endpoints import auth
from .endpoints import lastfm 

def register_blueprints(app):
    """Registra todos los blueprints de la API"""
    app.register_blueprint(auth.auth_bp)    
    app.register_blueprint(lastfm.lastfm_bp)