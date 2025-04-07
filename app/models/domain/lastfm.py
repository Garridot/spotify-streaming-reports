from app.core.database import db

class LastfmAccount(db.Model):
    __tablename__ = 'lastfm_accounts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lastfm_username = db.Column(db.String(50), nullable=False, unique=True)
    lastfm_session_key = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())   

    user = db.relationship('User', backref=db.backref('lastfm_account', uselist=False))