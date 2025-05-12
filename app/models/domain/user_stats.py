from app.core.database import db
from datetime import datetime

class DailyTracksPlayed(db.Model):
    __tablename__ = 'daily_track_plays'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tracks = db.Column(db.JSON)      
    date = db.Column(db.Date, nullable=False, index=True) 
    
    # Relationship
    user = db.relationship('User', backref=db.backref('daily_plays', lazy='dynamic'))


class WeeklyUserSummary(db.Model):
    __tablename__ = 'weekly_user_summary'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    week_start_date = db.Column(db.Date, nullable=False)
    week_end_date = db.Column(db.Date, nullable=False)
    top_tracks = db.Column(db.JSON)  
    top_artists = db.Column(db.JSON)
    top_genres = db.Column(db.JSON)
    extra_data = db.Column(db.JSON)

    # Relationship
    user = db.relationship('User', backref=db.backref('weekly_stats', lazy='dynamic'))