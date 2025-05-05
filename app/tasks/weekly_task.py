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
            'play_count': 'sum'
        }).reset_index()    
    
    # Group by date and song, adding duration and play count
    grouped_by_date = df.groupby(['date', 'song', 'artist']).agg({
        'total_duration_ms': 'sum',
        'play_count': 'sum'
    }).reset_index()

    # Find the most played songs by date (by play_count)
    most_played = grouped_by_date.loc[grouped_by_date.groupby('date')['play_count'].idxmax()]

    # Find the most played songs by date (by total_duration_ms)
    most_listened = grouped_by_date.loc[grouped_by_date.groupby('date')['total_duration_ms'].idxmax()]

    # Rename columns for clarity
    most_played = most_played[['date', 'song', 'artist', 'play_count']].rename(
        columns={'play_count': 'max_plays'})
    most_listened = most_listened[['date', 'song', 'artist', 'total_duration_ms']].rename(
        columns={'total_duration_ms': 'max_duration_ms'})

    # Convert duration to minutes for better reading
    most_listened['max_duration_min'] = most_listened['max_duration_ms'] / (1000 * 60)
    

    res = {}

    res["most listened to tracks (by total_duration_ms) of the week:"] = json.loads(grouped.sort_values(["total_duration_ms"], ascending=[False]).head(5).to_json(orient="records"))    
    res["most played to tracks (by play_count) of the week:"] = json.loads(grouped.sort_values(["play_count"], ascending=[False]).head(5).to_json(orient="records"))
    
    res["most played tracks by date:"] = json.loads(most_played.to_json(orient="records"))
    res["most listened tracks by date:"] = json.loads(most_listened.to_json(orient="records"))

    return res

def manage_artists_data(df):
    grouped = df.groupby(['artist']).agg({
            'total_duration_ms': 'sum',
            'play_count': 'sum'
        }).reset_index()   
    
    # Group by date and song, adding duration and play count
    grouped_by_date = df.groupby(['date', 'artist']).agg({
        'total_duration_ms': 'sum',
        'play_count': 'sum'
    }).reset_index()

    # Find the most played songs by date (by play_count)
    most_played = grouped_by_date.loc[grouped_by_date.groupby('date')['play_count'].idxmax()]

    # Find the most played songs by date (by total_duration_ms)
    most_listened = grouped_by_date.loc[grouped_by_date.groupby('date')['total_duration_ms'].idxmax()]

    # Rename columns for clarity
    most_played = most_played[['date', 'artist', 'play_count']].rename(
        columns={'play_count': 'max_plays'})
    most_listened = most_listened[['date', 'artist', 'total_duration_ms']].rename(
        columns={'total_duration_ms': 'max_duration_ms'})

    # Convert duration to minutes for better reading
    most_listened['max_duration_min'] = most_listened['max_duration_ms'] / (1000 * 60)    

    res = {}
    
    res["most listened to artists (by total_duration_ms) of the week:"] = json.loads(grouped.sort_values(["total_duration_ms"], ascending=[False]).head(5).to_json(orient="records"))    
    res["most played to artists (by play_count) of the week:"] = json.loads(grouped.sort_values(["play_count"], ascending=[False]).head(5).to_json(orient="records"))
    
    res["most played artists by date:"] = json.loads(most_played.to_json(orient="records"))
    res["most listened artists by date:"] = json.loads(most_listened.to_json(orient="records"))

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
    
    res["most listened to genres of the week:"] = json.loads(most_listened.head().to_json(orient="records"))
    res["most played to genres of the week:"] = json.loads(most_played.head().to_json(orient="records"))

    res["most listened to genres by date:"] = json.loads(most_listened_by_date.head().to_json(orient="records"))
    res["most played to genres by date:"] = json.loads(most_played_by_date.head().to_json(orient="records"))

    return res


def sync_all_users_weekly_register():
    """Task to synchronize the retrieval and storage of all user stats"""    
    users_repo = UserRepository(db.session).get_all_user()     
    weekly_register_repository = current_app.container.weekly_register_repository 
    last_day_of_week = datetime.now().date() - timedelta(days=1)
    first_day_of_week = last_day_of_week - timedelta(days=6)      

    for user in users_repo:
        try:
            retrieve_weekly_register = weekly_register_repository.retrieve_weekly_register(
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
                        "image": t["image"],
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
                top_genres = manage_genres_data(df)
            )

            logging.info(f"Successfully retrieved and saved the played tracks from {first_day_of_week} to {last_day_of_week} by user {user.id}.")
        except Exception as e:
            logging.error(f"An error occurred while attempting to store the played tracks from {first_day_of_week} to {last_day_of_week} by user {user.id}: {str(e)}")  

    

   
    
    # df_songs = tracks

    # df_songs.drop('artist_name', axis=1, inplace=True)

    # df_songs["artist_id"] = None
    # df_songs = df_songs.rename(columns={'artist_normalized': 'artist_name'})             

    # artists_info = df_songs.groupby(['artist_name']).agg({            
    #     'artist_id': 'last'
    # }).reset_index()

    # artists = json.loads(artists_info[['artist_name',"artist_id"]].to_json(orient="records"))            

    # artists_info = stats.sp_sync_functions._get_artists_played(artists)

    # df_artists = pd.DataFrame(artists_info)            

    # df_artists = df_artists.rename(columns={'artist': 'artist_name'})
    # df_artists['artist_name'] = df_artists['artist_name'].str.lower()     
                
    # df_merged = pd.merge(df_songs, df_artists[["artist_name",'artist_id', 'genres']], on='artist_name', how='left')
    
    # df_merged = df_merged.rename(columns={'artist_name': 'artist'})
    # df_merged = df_merged.rename(columns={'artist_id_y': 'artist_id'})
    # df_merged = df_merged.rename(columns={'song_name': 'song'})

    # df_merged.drop('artist_id_x', axis=1, inplace=True)
    # df_merged.drop('song_normalized', axis=1, inplace=True)
    # df_merged.drop('source', axis=1, inplace=True)       

    # grouped = df_merged.groupby(["artist", 'song'])

    # # Create a DataFrame to display the results
    # top_tracks = pd.DataFrame({ 
    #     "artist": grouped['artist'].first(),  
    #     "song": grouped['song'].first(),               
    #     'artist_id': grouped['artist_id'].last(),
    #     "total_duration_ms": None,
    #     "album": grouped["album"].last(),
    #     'play_count': grouped['played_at'].count(),
    #     "total_duration_min": None,
    #     'image': grouped["image"].last(), 
    #     'genres': grouped["genres"].last(),                
    # })

    # top_tracks['genres'] = top_tracks['genres'].apply(lambda x: x if isinstance(x, list) else []) 

    # top_tracks = top_tracks.to_json(orient="records")

    
    # date = datetime.now() - timedelta(days=4)   
    # daily_register_repository = current_app.container.daily_register_repository  

    # daily_register_repository.add_or_update_daily_register(
    #     user_id = 1,
    #     tracks = json.loads(top_tracks),                  
    #     date = date.date()
    # )  

    # res = daily_register_repository.retrieve_day_register(1)
    # [print(r.date) for r in res]



            