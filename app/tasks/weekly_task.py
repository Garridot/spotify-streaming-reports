from app.repositories.user_repository import UserRepository
from app.tasks.user_sync_service import CreateUserStats
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


def manage_tracks_data(df):
    grouped = df.groupby(['song', 'artist']).agg({
            'total_duration_ms': 'sum',
            'play_count': 'sum',
            'album': 'first',
            'image': 'first',
        }).reset_index()    
    
    # Group by date and song, adding duration and play count
    grouped_by_date = df.groupby(['date', 'song', 'artist']).agg({        
        'total_duration_ms': 'sum',
        'play_count': 'sum',
        'album': 'first',
        'image': 'first',
    }).reset_index()

    # Find the most played songs by date (by play_count)
    most_played = grouped_by_date.loc[grouped_by_date.groupby('date')['play_count'].idxmax()]

    # Find the most played songs by date (by total_duration_ms)
    most_listened = grouped_by_date.loc[grouped_by_date.groupby('date')['total_duration_ms'].idxmax()]

    # Rename columns for clarity
    most_played = most_played[['date', 'song', 'artist', 'play_count', 'album', 'image']].rename(
        columns={'play_count': 'max_plays'})
    most_listened = most_listened[['date', 'song', 'artist', 'total_duration_ms', 'album', 'image']].rename(
        columns={'total_duration_ms': 'max_duration_ms'})

    # Convert duration to minutes for better reading
    most_listened['max_duration_min'] = most_listened['max_duration_ms'] / (1000 * 60)
    
    res = {}
    res["most_listened_by_total_duration:"] = json.loads(grouped.sort_values(["total_duration_ms"], ascending=[False]).head(5).to_json(orient="records"))    
    res["most_played_by_play_count:"] = json.loads(grouped.sort_values(["play_count"], ascending=[False]).head(5).to_json(orient="records"))    
    res["most_played_tracks_by_date:"] = json.loads(most_played.to_json(orient="records"))
    res["most_listened_tracks_by_date:"] = json.loads(most_listened.to_json(orient="records"))
    
    return res

def manage_artists_data(df):
    grouped = df.groupby(['artist']).agg({
            'total_duration_ms': 'sum',
            'play_count': 'sum',            
            'artist_image': 'first',
        }).reset_index()   
    
    # Group by date and song, adding duration and play count
    grouped_by_date = df.groupby(['date', 'artist']).agg({
        'total_duration_ms': 'sum',
        'play_count': 'sum',       
        'artist_image': 'first',
    }).reset_index()

    # Find the most played songs by date (by play_count)
    most_played = grouped_by_date.loc[grouped_by_date.groupby('date')['play_count'].idxmax()]

    # Find the most played songs by date (by total_duration_ms)
    most_listened = grouped_by_date.loc[grouped_by_date.groupby('date')['total_duration_ms'].idxmax()]

    # Rename columns for clarity
    most_played = most_played[['date', 'artist', 'play_count', 'artist_image']].rename(
        columns={'play_count': 'max_plays'})
    most_listened = most_listened[['date', 'artist', 'total_duration_ms', 'artist_image']].rename(
        columns={'total_duration_ms': 'max_duration_ms'})

    # Convert duration to minutes for better reading
    most_listened['max_duration_min'] = most_listened['max_duration_ms'] / (1000 * 60)    

    res = {}    
    res["most_listened_by_total_duration:"] = json.loads(grouped.sort_values(["total_duration_ms"], ascending=[False]).head(5).to_json(orient="records"))    
    res["most_played_by_play_count:"] = json.loads(grouped.sort_values(["play_count"], ascending=[False]).head(5).to_json(orient="records"))    
    res["most_played_tracks_by_date:"] = json.loads(most_played.to_json(orient="records"))
    res["most_listened_tracks_by_date:"] = json.loads(most_listened.to_json(orient="records"))

    return res

def manage_genres_data(df):
    df_exploded = df.explode('genres')
    # Most played to genres of the week (by play_count)
    most_played = df_exploded.groupby('genres')['play_count'].sum().sort_values(ascending=False).reset_index()
    # Most listened to genres of the week (by total_duration_ms)
    most_listened = df_exploded.groupby('genres')['total_duration_ms'].sum().sort_values(ascending=False).reset_index()
    
    # Most played to genres by date (by play_count)
    most_played_by_date = df_exploded.groupby(['date', 'genres'])['play_count'].sum().sort_values(ascending=False).reset_index()
    # Most listened to genres by date (by total_duration_ms)
    most_listened_by_date = df_exploded.groupby(['date', 'genres'])['total_duration_ms'].sum().sort_values(ascending=False).reset_index()

    res = {}    
    res["most_listened_by_total_duration:"] = json.loads(most_listened.head().to_json(orient="records"))
    res["most_played_by_play_count:"] = json.loads(most_played.head().to_json(orient="records"))
    res["most_played_tracks_by_date:"] = json.loads(most_listened_by_date.head().to_json(orient="records"))
    res["most_listened_tracks_by_date:"] = json.loads(most_played_by_date.head().to_json(orient="records"))

    return res

def manage_extra_data(df):
   # Group by album, adding duration and play count
    grouped_by_album = df.groupby(['album']).agg({
        'total_duration_ms': 'sum',
        'play_count': 'sum',  
        'artist': 'first',     
        'image': 'first',
    }).reset_index()

    res = {}
    res["most_album_listened"] = json.loads(grouped_by_album.sort_values(["total_duration_ms"], ascending=[False]).head(1).to_json(orient="records"))
    res["most_album_played"] = json.loads(grouped_by_album.sort_values(["play_count"], ascending=[False]).head(1).to_json(orient="records"))

    return  res


def sync_all_users_weekly_register():
    """Task to synchronize the retrieval and storage of all user stats"""    
    users_repo = UserRepository(db.session).get_all_user()     
    weekly_register_repository = current_app.container.weekly_register_repository 
    last_day_of_week = datetime.now().date() - timedelta(days=1)
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
                        "artist": t["artist"],
                        "artist_id": t["artist_id"],
                        "song": t["song"],
                        "total_duration_ms": t["total_duration_ms"],
                        "play_count": t["play_count"],
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
 