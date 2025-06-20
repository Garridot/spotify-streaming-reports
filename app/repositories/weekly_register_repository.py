from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.domain.user_stats import DailyTracksPlayed
from app.models.domain.user_stats import WeeklyUserSummary

class WeeklyTracksPlayedRepository:
    def __init__(self, db: Session):
        self.db = db      

    def retrieve_weekly_tracks_played(self, user_id, start_date, end_date):
        weekly_register = self.db.query(DailyTracksPlayed).filter(            
            DailyTracksPlayed.user_id == user_id,
            DailyTracksPlayed.date >= start_date,
            DailyTracksPlayed.date <= end_date
        ).all() 
        
        return weekly_register

    def add_weekly_register(self, user_id, start_date, end_date, top_tracks, top_artists, top_genres, extra_data, report):
        weekly_register = WeeklyUserSummary(
            user_id = user_id, 
            week_start_date = start_date, 
            week_end_date = end_date, 
            top_tracks = top_tracks, 
            top_artists = top_artists, 
            top_genres = top_genres,
            extra_data = extra_data,
            report = report
            )   
        self.db.add(weekly_register)
        self.db.commit()
        return weekly_register   

    def retrieve_weekly_register(self, user_id, start_date, end_date):
        
        weekly_register = self.db.query(WeeklyUserSummary).filter(            
            WeeklyUserSummary.user_id == user_id,
            WeeklyUserSummary.week_start_date == start_date,
            WeeklyUserSummary.week_end_date == end_date
        ).first() 
        
        return weekly_register     

    def retrieve_all_weekly_register_by_user(self, user_id):
        
        weekly_register = (
            self.db.query(WeeklyUserSummary)
            .filter(WeeklyUserSummary.user_id == user_id,)
            .order_by(desc(WeeklyUserSummary.id))
            .all() 
        )
        
        return weekly_register  

    def retrieve_required_weekly_register_by_user(self, user_id, weekly_id):
        
        weekly_register = self.db.query(WeeklyUserSummary).filter(            
            WeeklyUserSummary.user_id == user_id,
            WeeklyUserSummary.id == weekly_id,
        ).first() 
        
        return weekly_register            