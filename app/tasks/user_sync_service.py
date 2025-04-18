from app.services.spotify_service import SpotifyService
from app.services.sp_oauth_service import SPOAuthService
from app.repositories.spotify_repository import SpotifyRepository
from app.services.lastfm_service import LastfmService
from app.repositories.lastfm_repository import LastfmRepository
from app.data_analyzer.data_manager import *
from app.core.database import db
import pandas as pd

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

    def _get_lastest_tracks_played(self):
        """
        Retrieve recently played tracks from Spotify by the user.
        Returns:        
            dataframe that containing the user's listening history recorded by Spotify.       
        """
        self._get_user_account_and_token() 
        tracks = self.sp_services.get_recently_played(self.token_user)        
        data_processed = load_and_preprocess_spotify(tracks)
        return data_processed

    def _get_artists_played(self, artists_id): 
        """Retrieve the information about the artists played by the user from Spotify."""
        self._get_user_account_and_token()           
        artists_info = self.sp_services.get_artist_info(artists_id, self.token_user)        
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
        self.fm_sync_functions = LastfmSyncData(user_id)
        self.user_stats = None

    def _get_user_stats(self):
        """      
        Function to synchronize the retrieval of the played tracks on Spotify and registered in Last.fm.  

        Workflow:
        1. Check if the user stats are already in the cache.
        2. If the user stats are not in the cache, retrieve the registered played tracks on Spotify and LastFM.
        3. store the user stats in the cache.
        """
        if self.user_stats is None:
            sp_data = self.sp_sync_functions._get_lastest_tracks_played()
            fm_data = self.fm_sync_functions._get_lastest_tracks_played()
            combined_data = get_combined_history(fm_data, sp_data)
            self.user_stats = combined_data

        return self.user_stats

    def _get_user_top_tracks(self):
        """
        Retrieve the top tracks played by the user for the day        
        """
        self._get_user_stats()
        top_tracks = get_top_tracks(self.user_stats, top_n=10)      
        return top_tracks.to_json(orient="records")

    def _get_user_top_artists(self):
        """
        Retrieve the top artists played by the user for the day        
        """
        self._get_user_stats()        
        top_artists = get_top_artists(self.user_stats, top_n=10)         
        return top_artists.to_json(orient="records")

    def _get_user_top_genres(self):
        """
        Retrieve the top genres played by the user for the day        
        """
        self._get_user_stats()
        top_artists = get_top_artists(self.user_stats, top_n=10)
        artists_id = top_artists["artist_id"].to_list()
        data = self.sp_sync_functions._get_artists_played(artists_id)    
        top_geners = get_top_geners(data, top_n=10)
        return top_geners.to_json(orient="records")
            
