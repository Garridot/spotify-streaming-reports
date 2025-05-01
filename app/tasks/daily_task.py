from app.tasks.user_sync_service import CreateUserStats 
from app.repositories.user_repository import UserRepository
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
            tracks = stats._get_user_tracks()  
            
            daily_register_repository.add_or_update_daily_register(
                user_id = user.id,
                top_tracks = json.loads(tracks),                  
                date = date.date()
            )  

            return logging.info(f"Success in retrieving and saving the played tracks on {date.date()} by the user {user.id}")
        except Exception as e:
            logging.error(f"An error occurred while attempting to store tracks played on {date.date()} by user {user.id}: {str(e)}")  