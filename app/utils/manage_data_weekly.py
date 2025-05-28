import json
import pandas as pd

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

    # Find the most played songs by date (by played_at)
    most_played = grouped_by_date.loc[grouped_by_date.groupby('date')['played_at'].idxmax()]

    # Find the most played songs by date (by duration_ms)
    most_listened = grouped_by_date.loc[grouped_by_date.groupby('date')['duration_ms'].idxmax()]

    # Rename columns for clarity
    most_played = most_played[['date', 'song_name', 'artist_name', 'played_at', 'album', 'image']]
    most_listened = most_listened[['date', 'song_name', 'artist_name', 'duration_ms', 'album', 'image']]

    # Convert duration to minutes for better reading
    most_listened['duration_min'] = most_listened['duration_ms'] / (1000 * 60)
    
    res = {}
    res["most_listened_by_total_duration:"] = json.loads(grouped.sort_values(["duration_ms"], ascending=[False]).head(5).to_json(orient="records"))    
    res["most_played_by_play_count:"] = json.loads(grouped.sort_values(["played_at"], ascending=[False]).head(5).to_json(orient="records"))    
    res["most_played_tracks_by_date:"] = json.loads(most_played.to_json(orient="records"))
    res["most_listened_tracks_by_date:"] = json.loads(most_listened.to_json(orient="records"))
    
    return res

def manage_artists_data(df):
    grouped = df.groupby(['artist_name']).agg({
            'duration_ms': 'sum',
            'played_at': 'count',            
            'artist_image': 'first',
        }).reset_index()   
    
    # Group by date and song, adding duration and play count
    grouped_by_date = df.groupby(['date', 'artist_name']).agg({
        'duration_ms': 'sum',
        'played_at': 'count',       
        'artist_image': 'first',
    }).reset_index()

    # Find the most played songs by date (by played_at)
    most_played = grouped_by_date.loc[grouped_by_date.groupby('date')['played_at'].idxmax()]

    # Find the most played songs by date (by duration_ms)
    most_listened = grouped_by_date.loc[grouped_by_date.groupby('date')['duration_ms'].idxmax()]

    # Rename columns for clarity
    most_played = most_played[['date', 'artist_name', 'played_at', 'artist_image']]

    most_listened = most_listened[['date', 'artist_name', 'duration_ms', 'artist_image']]

    # Convert duration to minutes for better reading
    most_listened['duration_min'] = most_listened['duration_ms'] / (1000 * 60)    

    res = {}    
    res["most_listened_by_total_duration:"] = json.loads(grouped.sort_values(["duration_ms"], ascending=[False]).head(5).to_json(orient="records"))    
    res["most_played_by_play_count:"] = json.loads(grouped.sort_values(["played_at"], ascending=[False]).head(5).to_json(orient="records"))    
    res["most_played_tracks_by_date:"] = json.loads(most_played.to_json(orient="records"))
    res["most_listened_tracks_by_date:"] = json.loads(most_listened.to_json(orient="records"))

    return res

def manage_genres_data(df):
    df_exploded = df.explode('genres')
    # Most played to genres of the week (by played_at)
    most_played = df_exploded.groupby('genres')['played_at'].sum().sort_values(ascending=False).reset_index()
    # Most listened to genres of the week (by duration_ms)
    most_listened = df_exploded.groupby('genres')['duration_ms'].sum().sort_values(ascending=False).reset_index()
    
    # Most played to genres by date (by played_at)
    most_played_by_date = df_exploded.groupby(['date', 'genres'])['played_at'].sum().sort_values(ascending=False).reset_index()
    # Most listened to genres by date (by duration_ms)
    most_listened_by_date = df_exploded.groupby(['date', 'genres'])['duration_ms'].sum().sort_values(ascending=False).reset_index()

    res = {}    
    res["most_listened_by_total_duration:"] = json.loads(most_listened.head().to_json(orient="records"))
    res["most_played_by_play_count:"] = json.loads(most_played.head().to_json(orient="records"))
    res["most_played_tracks_by_date:"] = json.loads(most_listened_by_date.head().to_json(orient="records"))
    res["most_listened_tracks_by_date:"] = json.loads(most_played_by_date.head().to_json(orient="records"))

    return res

def manage_extra_data(df, df2):
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
    total_tracks_last_week = df2.drop_duplicates(subset=['song_name']).shape[0]

    total_artist_this_week = df.drop_duplicates(subset=['artist_name']).shape[0]
    total_artist_last_week = df2.drop_duplicates(subset=['artist_name']).shape[0]

    total_time_this_week = df['duration_ms'].sum()
    total_time_last_week = df2['duration_ms'].sum()

    tracks_variation = {
        "total_track_variations" : f'{((total_tracks_this_week["total_songs_played"] - len(df2)) / len(df2)) * 100:.2f}%',
        "unique_track_variations": f'{((total_tracks_this_week["total_unique_songs"] - total_tracks_last_week) / total_tracks_last_week) * 100:.2f}%',
    }
    artists_variation = f'{((total_artist_this_week - total_artist_last_week) / total_artist_last_week) * 100:.2f}%'
    time_variation = f'{((total_time_this_week - total_time_last_week) / total_time_last_week) * 100:.2f}%'
  

    res = {}
    res["tracks_played_this_week"]= total_tracks_this_week
    res["artists_played_this_week"]= int(total_artist_this_week)
    res["time_listened_this_week"]= int(total_time_this_week)
    res["weekly_variation_tracks"] = tracks_variation
    res["weekly_variation_artists"] = artists_variation
    res["weekly_variation_time"] = time_variation
    res["most_album_listened"] = json.loads(grouped_by_album.sort_values(["duration_ms"], ascending=[False]).head(1).to_json(orient="records"))
    res["most_album_played"] = json.loads(grouped_by_album.sort_values(["played_at"], ascending=[False]).head(1).to_json(orient="records"))
    res["top_hours"] = json.loads(top_hours_df.to_json(orient="records"))
    res["top_day"] = json.loads(top_day_df.to_json(orient="records"))

    return  res