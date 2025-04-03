from app.core.database import db
from datetime import datetime

class User(db.Model):
    """Core user identity model"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)       

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"