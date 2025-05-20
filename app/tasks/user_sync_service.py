from app.services.spotify_service import SpotifyService
from app.services.sp_oauth_service import SPOAuthService
from app.repositories.spotify_repository import SpotifyRepository
from app.services.lastfm_service import LastfmService
from app.repositories.lastfm_repository import LastfmRepository
from app.data_analyzer.data_manager import *
from app.core.database import db
import pandas as pd
import json
import logging

logging.basicConfig(     
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class SpotifySyncData():
    """
    Class for synchronizing user authentication and retrieving the user's Spotify listening data.

    Parameters:
    -----------
        user_id (int): ID by the user  
    """
    def __init__(self, user_id: int):
        self.sp_services = SpotifyService()
        self.sp_oauth = SPOAuthService()
        self.sp_repository = SpotifyRepository(db.session)
        self.user_id = user_id 
        self.token_user = None

    def _get_user_account_and_token(self):
        """
        function to retrieve the user's Spotify access token and store it in cache.
        
        Workflow:
        1. Check if the token is already in the cache.
        2. If the token is not in the cache, retrieve the stored token from the database and save it in the cache.
        3. If the token has expired, request a new token from Spotify and store the new token in the cache.
        """
        account = self.sp_repository.get_by_user_id(self.user_id)          

        if not account: return False

        if self.token_user is None:
            if self.sp_oauth.is_token_expired(account.id):
                token = self.sp_oauth.refresh_access_token(account.id, account.refresh_token)
                self.token_user = token
            else:             
                self.token_user = account.access_token 

    def _get_lastest_tracks_played(self, after_timestamp = int):
        """
        Retrieve recently played tracks from Spotify by the user.
        Returns:        
            dataframe that containing the user's listening history recorded by Spotify.       
        """
        self._get_user_account_and_token()  
        tracks = self.sp_services.get_recently_played(self.token_user, after_timestamp)                
        if len(tracks) == 0: return None            
        data_processed = load_and_preprocess_spotify(tracks)               
        return data_processed
            

    def _get_artists_played(self, artists): 
        """Retrieve the information about the artists played by the user from Spotify."""
        self._get_user_account_and_token()           
        artists_info = self.sp_services.get_artist_info(artists, self.token_user)        
        return artists_info    


class LastfmSyncData():
    """
    Class to synchronize user authentication between Last.fm and retrieve the user's Spotify listening data registered on LastFM.
    
    Parameters:
    -----------
        user_id (int): ID by the user     
    
    """
    def __init__(self, user_id: int):
        self.fm_services = LastfmService()
        self.fm_repository = LastfmRepository(db.session)
        self.user_id = user_id 

    def _get_user_account(self):
        """
        function to retrieve the user's Lastfm data.
        """
        account = self.fm_repository.get_by_user_id(self.user_id)        
        if not account: return False
        
        return account  

    def _get_lastest_tracks_played(self):  
        """
        Retrieve the tracks played on Spotify recorded by Last.fm        
        Returns:        
            dataframe that containing the user's listening history of Spotify recorded by Last.fm     
        """
        account = self._get_user_account()  
        tracks = self.fm_services.get_diary_report(
            username    = account.lastfm_username,
            session_key = account.lastfm_session_key
            )
        data_processed = load_and_preprocess_lastfm(tracks)
        return data_processed     


class CreateUserStats():  
    """
    Class to create the stats of the user retrieving the data from Spotify and LastFM.    
    
    Parameters:
    -----------
        user_id (int): ID by the user     
    
    """  
    def __init__(self, user_id: int):
        self.sp_sync_functions = SpotifySyncData(user_id)
        self.user_stats = None

    def _get_user_stats(self, after_timestamp):
        """      
        Function to synchronize the retrieval of the played tracks on Spotify.  

        Workflow:
        1. Check if the user stats are already in the cache.
        2. If the user stats are not in the cache, retrieve the registered played tracks on Spotify.
        3. store the user stats in the cache.
        """
        if self.user_stats is None:
            sp_data = self.sp_sync_functions._get_lastest_tracks_played(after_timestamp=after_timestamp)
            self.user_stats = sp_data
        return self.user_stats

    def _get_user_tracks(self, after_timestamp):
        """
        Retrieve the top tracks played by the user for the day        
        """
        tracks = self._get_user_stats(after_timestamp)     
                
        try:
            grouped = tracks.groupby(['artist_normalized', 'artist_id']) 

            artists = pd.DataFrame({
                'artist_name': grouped['artist_name'].first(),
                'artist_id': grouped['artist_id'].first(),                       
            })

            artists_json = json.loads(artists[["artist_name","artist_id"]].to_json(orient="records"))        
            artists_data = self.sp_sync_functions._get_artists_played(artists_json) 

            df_songs = tracks
            df_artists = pd.DataFrame(artists_data)          

            df_artists = df_artists.rename(columns={'artist': 'artist_name'})

            # Normalize artist names
            df_songs['artist_name'] = df_songs['artist_name'].str.title()
            df_artists['artist_name'] = df_artists['artist_name'].str.title()

            # Perform a left merge
            merged_df = pd.merge(
                df_songs,
                df_artists,
                on='artist_name',
                how='left',
                suffixes=('', '_from_artists')
            )

            # Combine the artist id columns: prioritize the existing value in df songs, and if it's None, use the one in df_artists
            merged_df['artist_id'] = merged_df['artist_id'].fillna(merged_df['artist_id_from_artists'])

            # Delete the created temporary column
            merged_df = merged_df.drop(columns=['artist_id_from_artists'])

            merged_df['artist_image'] = merged_df['artist_image'].fillna(merged_df['image'])               

            return merged_df.to_json(orient="records")

        except Exception as e:            
            if str(e) == "'NoneType' object has no attribute 'groupby'":             
                return logging.error(f"Error retrieving the top tracks played by the user for the day: No found tracks played")
            else:
                return logging.error(f"Error retrieving the top tracks played by the user for the day: {e}")    

            
