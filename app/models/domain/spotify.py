from datetime import datetime
from app.core.database import db 

class SpotifyAccount(db.Model):
    """Spotify OAuth credentials storage"""    
    __tablename__ = 'spotify_accounts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    spotify_user_id = db.Column(db.String(50), nullable=False, unique=True)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=False)
    token_expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    user = db.relationship('User', backref=db.backref('spotify_account', uselist=False))

    def __init__(self, user_id: str, spotify_user_id: str, access_token: str, refresh_token: str, token_expires_at: datetime):
        self.user_id = user_id
        self.spotify_user_id = spotify_user_id
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expires_at = token_expires_at

    def __repr__(self):
        return f"<SpotifyAccount(user_id={self.user_id}, spotify_id={self.spotify_user_id})>"

    def is_token_expired(self) -> bool:
        """Business logic method to check token expiration"""
        return datetime.utcnow() >= self.token_expires_at