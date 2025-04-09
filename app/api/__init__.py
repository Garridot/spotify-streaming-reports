from .endpoints import spotify_oauth
from .endpoints import lastfm_oauth 
from .endpoints import lastfm_stats 
from .endpoints import auth 

def register_blueprints(app):
    """register all API blueprints"""
    app.register_blueprint(spotify_oauth.oauth_bp)    
    app.register_blueprint(lastfm_oauth.oauth_bp)
    app.register_blueprint(lastfm_stats.lastfm_stats_bp)
    app.register_blueprint(auth.auth_bp)