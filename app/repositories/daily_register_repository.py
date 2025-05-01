from sqlalchemy.orm import Session
from app.models.domain.user_stats import DailyTracksPlayed

class DailyTracksPlayedRepository:
    def __init__(self, db: Session):
        self.db = db        

    def add_or_update_daily_register(self, user_id, top_tracks, top_artists, top_genres, date):
        
        daily_register = DailyTracksPlayed(
            user_id = user_id,
            top_tracks = top_tracks, 
            date = date            
        )

        self.db.add(daily_register)
        self.db.commit()        
        return daily_register    

    def retrieve_day_register(self, user_id, date):

        day_register = self.db.query(DailyTracksPlayed).filter(
            (DailyTracksPlayed.user_id == user_id) |
            (DailyTracksPlayed.date == date)
        ).first()    

        return day_register

    def update_day_register(self, user_id, tracks, date):

        day_register = self.db.query(DailyTracksPlayed).filter(
            DailyTracksPlayed.user_id == user_id,
            DailyTracksPlayed.date == date
        ).first()
        
        if day_register:
            day_register.top_tracks = tracks   

        self.db.commit()
        self.db.refresh(day_register)    

        return day_register   
        
        
