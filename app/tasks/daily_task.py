from app.workers.user_sync_service import CreateUserStats, LastfmSyncData
from app.repositories.user_repository import UserRepository
from app.repositories.daily_register_repository import DailyTracksPlayedRepository
from flask import current_app
from app.core.database import db
from datetime import datetime, timedelta
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def sync_all_users_daily_register():
    """Task to synchronize the retrieval and storage of all user stats"""
    users_repo = UserRepository(db.session).get_all_user()     
    daily_register_repository = current_app.container.daily_register_repository  
    date = datetime.now() - timedelta(days=1)

    for user in users_repo:       
        try:
            stats = CreateUserStats(user.id)  
            
            tracks = stats._get_user_top_tracks()
            artists = stats._get_user_top_artists()
            genres = stats._get_user_top_genres()   

            daily_register_repository.add_daily_register(
                user_id = user.id,
                top_tracks = json.loads(tracks),  
                top_artists = json.loads(artists),
                top_genres = json.loads(genres),
                date = date.date()
            )  
            logging.info(f"Success in retrieving and saving the played tracks on {date.date()} by the user {user.id}")
        except Exception as e:
            logging.error(f"An error occurred while attempting to store tracks played on {date.date()} by user {user.id}: {str(e)}")  