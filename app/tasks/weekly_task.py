from app.repositories.user_repository import UserRepository
from app.tasks.user_sync_service import CreateUserStats
from app.utils.manage_data_weekly import *
from app.tasks.generate_report import generate_deepseek_report
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
    daily_register_repository = current_app.container.daily_register_repository 
    last_day_of_week = datetime.utcnow().date() - timedelta(days=1)
    first_day_of_week = last_day_of_week - timedelta(days=6)      

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

            tracks_data = manage_tracks_data(df) 
            artists_data = manage_artists_data(df) 
            genres_data = manage_genres_data(df)

            last_day_of_last_week = last_day_of_week - timedelta(days=7)     
            first_day_of_last_week = last_day_of_last_week - timedelta(days=7)

            retrieve_last_week_register =  weekly_register_repository.retrieve_weekly_register(
                user_id = user.id,
                start_date = first_day_of_last_week,  
                end_date = last_day_of_last_week,                
            ) 

            if retrieve_last_week_register: 
                last_week = retrieve_last_week_register.extra_data  
            else:
                last_week = None    

            extra_data = manage_extra_data(df, last_week)             

            data_report = [
                {"top_tracks_of_the_week": clean_data_custom(tracks_data)},
                {"top_artists_of_the_week": clean_data_custom(artists_data)},
                {"top_genres_data_of_the_week": clean_data_custom(genres_data)},
                {"extra_data_of_the_week": extra_data}                
            ]

            report = generate_deepseek_report(data_report)
            
            weekly_register_repository.add_weekly_register(
                user_id = user.id, 
                start_date = first_day_of_week, 
                end_date = last_day_of_week, 
                top_tracks = tracks_data, 
                top_artists = artists_data, 
                top_genres = genres_data,
                extra_data = extra_data,
                report = json.loads(report)
            )

            for register in retrieve_weekly_register:
                                
                daily_register_repository.delete_daily_register(
                    user_id = user.id,
                    date = register.date, 
                ) 


            logging.info(f"Successfully retrieved and saved the played tracks from {first_day_of_week} to {last_day_of_week} by user {user.id}.")
        except Exception as e:
            logging.error(f"An error occurred while attempting to store the played tracks from {first_day_of_week} to {last_day_of_week} by user {user.id}: {str(e)}")
 