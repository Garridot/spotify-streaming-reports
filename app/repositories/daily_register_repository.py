from sqlalchemy.orm import Session
from app.models.domain.user_stats import DailyTracksPlayed

class DailyTracksPlayedRepository:
    def __init__(self, db: Session):
        self.db = db        

    def add_daily_register(self, user_id, tracks, artists, genres, date):
        data = DailyTracksPlayed(
            user_id = user_id,
            top_tracks = tracks,  
            top_artists = artists,
            top_genres = genres,
            date = date            
        )
        self.db.add(data)
        self.db.commit()
        self.db.refresh(data)  
        return data

    def retrieve_weekly_register(self, start_date, end_date):
        weekly_register = self.db.query(DailyTracksPlayed).filter(            
            DailyTracksPlayed.user_id == user_id,
            DailyTracksPlayed.date >= start_date,
            DailyTracksPlayed.date <= end_date
        ).all() 
        
        return weekly_register
        
        
