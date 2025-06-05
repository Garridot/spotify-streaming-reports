import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Spotify
    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
    SPOTIFY_SCOPES = 'user-read-email user-read-private'
    
    # Last.fm
    LASTFM_API_KEY = os.getenv('LASTFM_API_KEY')
    LASTFM_API_SECRET = os.getenv('LASTFM_API_SECRET')
    LASTFM_CALLBACK_URL= os.getenv("LASTFM_CALLBACK_URL")

    SECRET_KEY: str = os.getenv("SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"

    CLOUDAMQP_URL = os.getenv('CLOUDAMQP_URL')

    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

    # Flask-Mail (Gmail SMTP)
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///spotify.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}    
