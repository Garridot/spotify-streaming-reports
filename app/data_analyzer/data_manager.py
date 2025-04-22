import pandas as pd
import numpy as np
from datetime import datetime
import re
import unicodedata
from datetime import datetime, timedelta


def normalize_text(text):
    """
    Base function for text normalization that preserves all alphabets
    Args:
        text (str): text to normalize
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Unicode Normalization (NFKC)
    text = unicodedata.normalize('NFKC', text)
    
    # Remove specific unwanted characters (keeping all languages)
    text = re.sub(r'[\[\]\'\"]', '', text)
    
    # Convert to lowercase (works with Unicode)
    text = text.lower()
    
    # Keep:
    # - All letters in any language (including kanji, Cyrillic, etc.)
    # - Numbers
    # - Spaces
    # - Hyphens (but not other symbols)
    # 
    # We use Unicode categories:
    # L* = all letters
    # N* = all numbers
    # Zs = space separator
    text = ''.join(
        c for c in text 
        if unicodedata.category(c)[0] in ('L', 'N')  
        or unicodedata.category(c) == 'Zs' 
        or c in ('-', ' ') 
    )
    
    # Normalize spaces (convert multiple spaces to one)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def normalize_artist_name(artist):
    """
    Normalizes artist names
    Args:
        artist (str): text to normalize
    """
    if isinstance(artist, list):
        artist = ', '.join(artist)
    return normalize_text(artist)


def normalize_song_name(song):
    """
    Normalizes song names
    Args:
        song (str): text to normalize
    """
    song = str(song)
    # Primero eliminar paréntesis y versiones
    song = re.sub(r'\([^)]*\)', '', song)
    song = re.sub(r' - .*$', '', song)
    return normalize_text(song)


def load_and_preprocess_lastfm(data):
    """
    Load and process data received from Last.fm
    - Rename columns and normalize dates
    - Normalize title of artists and songs
    - Select and sort relevant columns
    """    
    processed_tracks = []
    for track in data:
        # Convertir el timestamp Unix a datetime
        uts = int(track['date']['uts'])
        played_at = datetime.fromtimestamp(uts)
        
        processed_tracks.append({
            'artist': track['artist']['#text'],
            'song': track['name'],
            'album': track['album']['#text'],
            'played_at': played_at,
            'timestamp': uts,            
            'image': next((img['#text'] for img in track['image'] if img['size'] == 'medium'), None),            
        })

    df = pd.DataFrame(processed_tracks)      
    
    # Rename columns and normalize dates
    df = df.rename(columns={'artist': 'artist_name', 'song': 'song_name','image_medium':'image'})
    df['played_at'] = pd.to_datetime(df['played_at'], utc=True).dt.tz_localize(None)
    
    # Normalize title of artists and songs
    df['artist_normalized'] = df['artist_name'].apply(normalize_artist_name)
    df['song_normalized'] = df['song_name'].apply(normalize_song_name)
    
    # Select and sort relevant columns
    cols = ['artist_name', 'song_name', 'album', 'played_at',
            'image','artist_normalized', 'song_normalized']
    df = df[[col for col in cols if col in df.columns]]
    df['source'] = 'lastfm'
    
    return df


def load_and_preprocess_spotify(data):
    """
    Load and process data received from Spotify
    - Rename columns and normalize dates
    - Normalize title of artists and songs
    - Select and sort relevant columns
    """
    df = pd.DataFrame(data)      
    
    # Rename columns and normalize dates
    df = df.rename(columns={
        'name': 'song_name',
        'artists': 'artist_name',
        'artists_id': 'artist_id'
    })
    df['played_at'] = pd.to_datetime(df['played_at'], utc=True).dt.tz_localize(None)
    
    # Normalize title of artists and songs
    df['artist_name'] = df['artist_name'].str.replace(r'[\[\]\'\"]', '', regex=True)
    df['artist_normalized'] = df['artist_name'].apply(normalize_artist_name)
    df['song_normalized'] = df['song_name'].apply(normalize_song_name)
    
    # Select and sort relevant columns
    cols = [ 'song_name', 'artist_name', 'artist_id', 'album', 'played_at',
            'duration_ms', 'artist_normalized', 'song_normalized', "image"]
    df = df[cols]
    df['source'] = 'spotify'
    
    return df


def combine_datasets(lastfm_df, spotify_df):
    """
    Combines dataframes according to the following criteria:
    - Keep the entire Spotify dataframe
    - Keep all Last.fm rows before the listen date of the first recorded Spotify track
    Args:
        - lastfm_df: dataframe containing the user's listening history recorded by Last.fm. 
        - spotify_df: dataframe containing the user's listening history recorded by Spotify.
    Returns: 
        - dataframe that enhances the information collected from Spotify by including data obtained from LastFM.
    """
    # Get the latest Spotify date 
    cutoff_date = spotify_df.iloc[0]['played_at']

    date = datetime.now().date() - timedelta(days=1)
    # filter the rows of the data frame that correspond to the previous day
    spotify_df = spotify_df[spotify_df['played_at'].dt.date == date]
    
    # Filter Last.fm by previous dates
    lastfm_previous = lastfm_df[lastfm_df['played_at'] < cutoff_date].copy()
    
    # Combine the data
    combined = pd.concat([spotify_df, lastfm_previous], ignore_index=True)
    
    # Sort by date descending
    combined = combined.sort_values('played_at', ascending=False)
    
    return combined


def get_combined_history(lastfm_df, spotify_df):
    """
    Function to get the combined user history
    Args:
        - lastfm_df: dataframe containing the user's listening history recorded by Last.fm. 
        - spotify_df: dataframe containing the user's listening history recorded by Spotify.
    Returns:
        Updated SpotifyAccount entity

    """
    
    combined_df = combine_datasets(lastfm_df, spotify_df)
    
    # Select and sort relevant columns
    cols_order = [
        'song_normalized', 'artist_normalized', 'artist_id',
        'album', 'played_at', 'duration_ms', 'source',  
        'song_name', 'artist_name','image',
    ]
    cols_order = [col for col in cols_order if col in combined_df.columns]
    
    return combined_df[cols_order].sort_values('played_at')


def get_top_tracks(combined_df, top_n):
    """
   Obtains the user's most-played tracks, considering:
        - Playback frequency (played_at count)
        - In case of a tie, total listening duration (sum of duration_ms)

    Args:
        combined_df (pd.DataFrame): Combined DataFrame of Spotify and Last.fm
        top_n (int): Number of top tracks to return

    Returns:
        pd.DataFrame: DataFrame with the most-played tracks, sorted
    """
    # Check if duration data exists (Spotify)
    has_duration = 'duration_ms' in combined_df.columns
    
    # Group by artist and song (using normalized names for better matching)
    grouped = combined_df.groupby(['artist_normalized', 'song_normalized'])
    
    # Create a DataFrame to display the results
    top_tracks = pd.DataFrame({
        'artist': grouped['artist_name'].first(),
        'artist_id': grouped['artist_id'].first(),
        'song': grouped['song_name'].first(),
        'album': grouped['album'].first(),
        'play_count': grouped['played_at'].count(),
        'image': grouped['image'].first(),        
    })
    
    # Si tenemos datos de duración, calcular la duración total por canción
    if has_duration:
        top_tracks['total_duration_ms'] = grouped['duration_ms'].sum()
    else:
        top_tracks['total_duration_ms'] = 0
    
    # If duration data exists, calculate the total duration per song
    top_tracks = top_tracks.sort_values(
        ['play_count', 'total_duration_ms'], 
        ascending=[False, False]
    )    
    
    top_tracks = top_tracks.reset_index(drop=True)
    
    # Convert duration from milliseconds to minutes for better readability
    top_tracks['total_duration_min'] = top_tracks['total_duration_ms'] / 60000
    top_tracks['total_duration_min'] = top_tracks['total_duration_min'].round(2)
    
    # Select and sort relevant columns
    result_cols = ['artist', 'artist_id', 'song', 'album','play_count', 'total_duration_min', 'image']
    
    if has_duration:
        result_cols.insert(3, 'total_duration_ms')
    
    return top_tracks[result_cols]

def get_top_artists(combined_df, top_n):
    """
    Obtains the user's most-played artists, considering:
        - Playback frequency (played_at count)
        - In case of a tie, total listening duration (sum of duration_ms)

    Args:
        combined_df (pd.DataFrame): Combined DataFrame of Spotify and Last.fm
        top_n (int): Number of top artists to return

    Returns:
        pd.DataFrame: DataFrame with the most-played artists, sorted
    """
    has_duration = 'duration_ms' in combined_df.columns
    
    # Group by artist 
    grouped = combined_df.groupby(['artist_name'])
    
    # Create a DataFrame to display the results
    top_tracks = pd.DataFrame({
        'artist_name': grouped['artist_normalized'].first(),
        'artist_id': grouped['artist_id'].first(),
        'play_count': grouped['played_at'].count(),
    })   
    
    if has_duration:
        top_tracks['total_duration_ms'] = grouped['duration_ms'].sum()
    else:
        top_tracks['total_duration_ms'] = 0
    
    # Sort first by play count and then by total duration
    top_tracks = top_tracks.sort_values(
        ['play_count', 'total_duration_ms'], 
        ascending=[False, False]
    )   
    
    return top_tracks.sort_values('play_count', ascending=False)

def get_top_geners(data, top_n):    
    """
    Obtains the user's most-played geners, considering:
        - Playback frequency (played_at count)

    Args:
        data (JSON): Information in JSON format with the necessary data 
        top_n (int): Number of top geners to return

    Returns:
        pd.DataFrame: DataFrame with the most-played geners, sorted
    """    
    df = pd.DataFrame(data)
    # Explode the genre list so that each genre is in a separate row
    genres_exploded = df['genres'].explode()
    # Count the frequency of each gender
    genre_counts = genres_exploded.value_counts().reset_index()
    genre_counts.columns = ['genres', 'play_count']

    return genre_counts

