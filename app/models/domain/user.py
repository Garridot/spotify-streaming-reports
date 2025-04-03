from app.core.database import db
from datetime import datetime

class User(db.Model):
    """Core user identity model"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    spotify_id = db.Column(db.String(50), unique=True, nullable=True)  
    
    # Relationship
    spotify_account = db.relationship(
        'SpotifyAccount', 
        back_populates='user',
        uselist=False,
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"