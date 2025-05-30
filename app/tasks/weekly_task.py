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
    last_day_of_week = datetime.utcnow().date() - timedelta(days=4)     
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

            tracks_data = manage_tracks_data(df), 
            artists_data = manage_artists_data(df), 
            genres_data = manage_genres_data(df),
            extra_data = [
                    {'tracks_played_this_week': {'total_songs_played': 235, 'total_unique_songs': 122}, 'artists_played_this_week': 45, 'time_listened_this_week': 48884588, 'weekly_variation_tracks': {'total_track_variations': '8.29%', 'unique_track_variations': '-17.01%'}, 'weekly_variation_artists': '-34.78%', 'weekly_variation_time': '-2.60%', 'most_album_listened': [{'album': 'The Beatles 1967 – 1970 (2023 Edition)', 'duration_ms': 12724380, 'played_at': 54, 'artist_name': 'The Beatles', 'image': 'https://i.scdn.co/image/ab67616d0000b2732ad20d4688bdc999413ece39'}], 'most_album_played': [{'album': 'The Beatles 1967 – 1970 (2023 Edition)', 'duration_ms': 12724380, 'played_at': 54, 'artist_name': 'The Beatles', 'image': 'https://i.scdn.co/image/ab67616d0000b2732ad20d4688bdc999413ece39'}], 'top_hours': [{'hours': '21:00', 'songs_played': 44}, {'hours': '00:00', 'songs_played': 27}, {'hours': '20:00', 'songs_played': 27}, {'hours': '15:00', 'songs_played': 26}, {'hours': '19:00', 'songs_played': 16}], 'top_day': [{'day': 'Sunday', 'songs_played': 97}]}
                ]    

            data_report = [
                {"top_tracks_of_the_week": clean_data_custom(tracks_data[0])},
                {"top_artists_of_the_week": clean_data_custom(artists_data[0])},
                {"top_genres_data_of_the_week": clean_data_custom(genres_data[0])},
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
                report = report
            )


            logging.info(f"Successfully retrieved and saved the played tracks from {first_day_of_week} to {last_day_of_week} by user {user.id}.")
        except Exception as e:
            logging.error(f"An error occurred while attempting to store the played tracks from {first_day_of_week} to {last_day_of_week} by user {user.id}: {str(e)}")
 