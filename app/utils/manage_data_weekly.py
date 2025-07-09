import json
import pandas as pd

day_order = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6}

def manage_tracks_data(df):
    grouped = df.groupby(['song_name', 'artist_name']).agg({
            'duration_ms': 'sum',
            'played_at': 'count',
            'album': 'first',
            'image': 'first',
        }).reset_index()    
    
    # Group by date and song, adding duration and play count
    grouped_by_date = df.groupby(['date', 'song_name', 'artist_name']).agg({        
        'duration_ms': 'sum',
        'played_at': 'count',
        'album': 'first',
        'image': 'first',
    }).reset_index()

    df["day"] = pd.to_datetime(df["date"]).dt.day_name()

    # Group by date and song, adding duration and play count
    grouped_by_date = df.groupby(['day', 'song_name', 'artist_name']).agg({
        'duration_ms': 'sum',
        'played_at': 'count', 
        'album': 'first',      
        'image': 'first',
    }).reset_index()

    idx = grouped_by_date.groupby('day')['duration_ms'].idxmax()
    most_listened = grouped_by_date.loc[idx].reset_index(drop=True) 

    res = {}
    res["most_listened_by_total_duration"] = json.loads(grouped.sort_values(["duration_ms"], ascending=[False]).head(5).to_json(orient="records"))    
    res["most_played_by_play_count"] = json.loads(grouped.sort_values(["played_at"], ascending=[False]).head(5).to_json(orient="records")) 
    
    most_listened = most_listened.sort_values('day', key=lambda x: x.map(day_order))
    res["most_listened_tracks_by_date"] = json.loads(most_listened.to_json(orient="records"))
    
    return res

def manage_artists_data(df):
    grouped = df.groupby(['artist_name']).agg({
            'duration_ms': 'sum',
            'played_at': 'count',            
            'artist_image': 'first',
        }).reset_index()  

    df["day"] = pd.to_datetime(df["date"]).dt.day_name()

    # Group by date and song, adding duration and play count
    grouped_by_date = df.groupby(['day', 'artist_name']).agg({
        'duration_ms': 'sum',
        'played_at': 'count',       
        'artist_image': 'first',
    }).reset_index()

    idx = grouped_by_date.groupby('day')['duration_ms'].idxmax()
    most_listened = grouped_by_date.loc[idx].reset_index(drop=True)    

    res = {}    
    res["most_listened_by_total_duration"] = json.loads(grouped.sort_values(["duration_ms"], ascending=[False]).head(5).to_json(orient="records"))    
    res["most_played_by_play_count"] = json.loads(grouped.sort_values(["played_at"], ascending=[False]).head(5).to_json(orient="records"))    
    
    most_listened = most_listened.sort_values('day', key=lambda x: x.map(day_order))
    res["most_listened_artists_by_date"] = json.loads(most_listened.to_json(orient="records"))

    return res

def manage_genres_data(df):
    df_exploded = df.explode('genres')    
    # Most listened to genres of the week (by duration_ms)
    most_listened = df_exploded.groupby('genres')['duration_ms'].sum().sort_values(ascending=False).reset_index()    
    
    df_exploded["day"] = pd.to_datetime(df_exploded["date"]).dt.day_name()
    
    grouped = df_exploded.groupby(['day', 'genres'], as_index=False)['duration_ms'].sum()    
    idx = grouped.groupby('day')['duration_ms'].idxmax()
    # Most listened to genres by date (by duration_ms)
    most_listened_by_date = grouped.loc[idx].reset_index(drop=True)    

    res = {}    
    res["most_listened_by_total_duration"] = json.loads(most_listened.head().to_json(orient="records"))  

    most_listened_by_date = most_listened_by_date.sort_values('day', key=lambda x: x.map(day_order)) 
    res["most_listened_genres_by_date"] = json.loads(most_listened_by_date.head().to_json(orient="records"))

    return res

def manage_extra_data(df, last_week):
   # Group by album, adding duration and play count
    grouped_by_album = df.groupby(['album']).agg({
        'duration_ms': 'sum',
        'played_at': 'count',  
        'artist_name': 'first',     
        'image': 'first',
    }).reset_index()

    # Convert milliseconds to seconds (UNIX timestamp uses seconds)
    df['datetime'] = pd.to_datetime(df['played_at'], unit='ms')
    
    # Extract only the hour from the datetime (in HH format)
    df['hours'] = df['datetime'].dt.hour

    # Extract only the name day from the datetime 
    df['day_of_week'] = df['datetime'].dt.day_name()    

    # Count the most played hours
    top_hours_df = df['hours'].value_counts().head(5).reset_index()
    top_hours_df.columns = ['hours', 'songs_played']

    # Format the 'hour' column as a string in the format HH:MM.
    top_hours_df['hours'] = top_hours_df['hours'].apply(lambda h: f"{h:02d}:00")
    
    # Count the most played day
    top_day_df = df['day_of_week'].value_counts().head(1).reset_index()
    top_day_df.columns = ['day', 'songs_played']   

    total_tracks_this_week = {
        "total_songs_played": int(len(df)),
        "total_unique_songs": int(df.drop_duplicates(subset=['song_name']).shape[0])
        }

    total_artist_this_week = df.drop_duplicates(subset=['artist_name']).shape[0]  
    total_time_this_week = df['duration_ms'].sum()   
  

    res = {}
    res["tracks_played_this_week"]= total_tracks_this_week
    res["artists_played_this_week"]= int(total_artist_this_week)
    res["time_listened_this_week"]= int(total_time_this_week) 
    res["most_album_listened"] = json.loads(grouped_by_album.sort_values(["duration_ms"], ascending=[False]).head(1).to_json(orient="records"))
    res["top_hours"] = json.loads(top_hours_df.to_json(orient="records"))
    res["top_day"] = json.loads(top_day_df.to_json(orient="records"))

    
    if last_week:
    
        total_tracks_last_week = int(last_week["tracks_played_this_week"]["total_unique_songs"])
        total_artist_last_week = int(last_week["artists_played_this_week"])    
        total_time_last_week = int(last_week['time_listened_this_week'])

        tracks_variation = {
            "total_track_variations" : f'{((total_tracks_this_week["total_songs_played"] - int(last_week["tracks_played_this_week"]["total_songs_played"])) / int(last_week["tracks_played_this_week"]["total_songs_played"])) * 100:.2f}%',
            "unique_track_variations": f'{((total_tracks_this_week["total_unique_songs"] - total_tracks_last_week) / total_tracks_last_week) * 100:.2f}%',
        }
        artists_variation = f'{((total_artist_this_week - total_artist_last_week) / total_artist_last_week) * 100:.2f}%'
        time_variation = f'{((total_time_this_week - total_time_last_week) / total_time_last_week) * 100:.2f}%'


        res["weekly_variation_tracks"] = tracks_variation
        res["weekly_variation_artists"] = artists_variation
        res["weekly_variation_time"] = time_variation

    return  res

def manage_last_activity(data):

    df = pd.DataFrame(json.loads(data))

    grouped_tracks = df.groupby(['song_name', 'artist_name']).agg({
        'duration_ms': 'sum',
        'played_at': 'count',
        'album': 'first',
        'image': 'first',
    }).reset_index()     

    grouped_artists = df.groupby(['artist_name']).agg({
        'duration_ms': 'sum',
        'played_at': 'count',            
        'artist_image': 'first',
    }).reset_index() 

    grouped_by_album = df.groupby(['album']).agg({
        'duration_ms': 'sum',
        'played_at': 'count',  
        'artist_name': 'first',     
        'image': 'first',
    }).reset_index()

    df_exploded = df.explode('genres')   
    most_genres_listened = df_exploded.groupby('genres')['duration_ms'].sum().sort_values(ascending=False).reset_index()

    res = {}
    res["most_tracks_listened"] = json.loads(grouped_tracks.sort_values(["duration_ms"], ascending=[False]).head(5).to_json(orient="records"))    
    res["most_artists_listened"] = json.loads(grouped_artists.sort_values(["duration_ms"], ascending=[False]).head(5).to_json(orient="records"))    
    res["most_genres_listened"] = json.loads(most_genres_listened.head().to_json(orient="records")) 
    res["most_album_listened"] = json.loads(grouped_by_album.sort_values(["duration_ms"], ascending=[False]).head(1).to_json(orient="records"))

    return res

def clean_data_custom(data):
    default_fields_to_remove = {'album', 'image','duration_min','artist_image'}
    
    # Special rules: key → additional fields to delete
    special_rules = {
        'most_listened_by_total_duration': {'played_at'},  
        'most_played_by_play_count': {'duration_ms'},     
    }
    
    cleaned_data = {}
    for category, tracks in data.items():
        # Fields to remove = default fields + additional fields (if the key has a rule)
        fields_to_remove = default_fields_to_remove | special_rules.get(category, set())
        
        cleaned_tracks = [
            {k: v for k, v in track.items() if k not in fields_to_remove}
            for track in tracks
        ]
        cleaned_data[category] = cleaned_tracks
    return cleaned_data