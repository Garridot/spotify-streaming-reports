from .endpoints import auth

def register_blueprints(app):
    """Registra todos los blueprints de la API"""
    app.register_blueprint(auth.auth_bp)