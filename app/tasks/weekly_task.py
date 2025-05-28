from app.repositories.user_repository import UserRepository
from app.tasks.user_sync_service import CreateUserStats
from app.utils.manage_data_weekly import *
from flask import current_app
from app.core.database import db
from datetime import datetime, timedelta
import logging
import json
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def sync_all_users_weekly_register():
    """Task to synchronize the retrieval and storage of all user stats"""    
    users_repo = UserRepository(db.session).get_all_user()     
    weekly_register_repository = current_app.container.weekly_register_repository 
    last_day_of_week = datetime.utcnow().date() - timedelta(days=2)     
    first_day_of_week = last_day_of_week - timedelta(days=7)

    for user in users_repo:
        try:
            retrieve_weekly_register = weekly_register_repository.retrieve_weekly_tracks_played(
                user_id = user.id,
                start_date = first_day_of_week,  
                end_date = last_day_of_week,                
            ) 

            r_list = []      

            for r in retrieve_weekly_register:
                data = {
                    "user_id" : r.user_id,
                    "tracks" : r.tracks,                      
                    "date" : r.date
                }
                r_list.append(data)  

            res = r_list

            tracks_list = []         

            for (data,index) in zip(res,range(0,len(res))):
                date = res[index]["date"]
                for t in data["tracks"]:
                    d = {
                        "artist_name": t["artist_name"],
                        "artist_id": t["artist_id"],
                        "song_name": t["song_name"],
                        "duration_ms": t["duration_ms"],
                        "played_at": t["played_at"],
                        "album": t["album"],
                        "image": t["image"],
                        "artist_image": t["artist_image"],
                        "genres": t["genres"],
                        "date": date
                    }
                    tracks_list.append(d) 

            df = pd.DataFrame(tracks_list)             

            weekly_register_repository.add_weekly_register(
                user_id = user.id, 
                start_date = first_day_of_week, 
                end_date = last_day_of_week, 
                top_tracks = manage_tracks_data(df), 
                top_artists = manage_artists_data(df), 
                top_genres = manage_genres_data(df),
                extra_data = manage_extra_data(df)
            )

            logging.info(f"Successfully retrieved and saved the played tracks from {first_day_of_week} to {last_day_of_week} by user {user.id}.")
        except Exception as e:
            logging.error(f"An error occurred while attempting to store the played tracks from {first_day_of_week} to {last_day_of_week} by user {user.id}: {str(e)}")
 