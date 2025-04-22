from sqlalchemy.orm import Session
from app.models.domain.user_stats import DailyTracksPlayed

class DailyTracksPlayedRepository:
    def __init__(self, db: Session):
        self.db = db        

    def add_or_update_daily_register(self, user_id, top_tracks, top_artists, top_genres, date):
        daily_register = self.retrieve_day_register(user_id, date)
        
        if daily_register:
            daily_register.top_tracks = top_tracks,  
            daily_register.top_artists = top_artists,
            daily_register.top_genres = top_genres,
        else:    
            daily_register = DailyTracksPlayed(
                user_id = user_id,
                top_tracks = top_tracks,  
                top_artists = top_artists,
                top_genres = top_genres,
                date = date            
            )

            self.db.add(daily_register)
        self.db.commit()
        self.db.refresh(daily_register)  
        return daily_register

    def retrieve_weekly_register(self, start_date, end_date):
        weekly_register = self.db.query(DailyTracksPlayed).filter(            
            DailyTracksPlayed.user_id == user_id,
            DailyTracksPlayed.date >= start_date,
            DailyTracksPlayed.date <= end_date
        ).all() 
        
        return weekly_register

    def retrieve_day_register(self, user_id, date):

        day_register = self.db.query(DailyTracksPlayed).filter(
            (DailyTracksPlayed.user_id == user_id) |
            (DailyTracksPlayed.date == date)
        ).first()    

        return day_register
        
        
