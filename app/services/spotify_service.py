import os
from typing import Dict, Optional
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from app.core.config import Config
from app.models.schemas.spotify import TokenResponse

class SpotifyService:
    def __init__(self):       
        self.oauth = SpotifyOAuth(
            client_id=Config.SPOTIFY_CLIENT_ID,
            client_secret=Config.SPOTIFY_CLIENT_SECRET,
            redirect_uri=Config.SPOTIFY_REDIRECT_URI,
            scope="user-read-email user-read-private user-top-read user-read-recently-played",  
        )
    
    def get_oauth_url(self) -> str:
        """
        Generate Spotify authorization URL
        Args:
            state: Optional CSRF protection state
        Returns:
            Spotify authorization URL
        """
        auth_url = self.oauth.get_authorize_url()
        return auth_url
    
    def exchange_code_for_tokens(self, code: str) -> TokenResponse:
        """
        Exchange authorization code for access/refresh tokens
        Args:
            code: Authorization code from Spotify
        Returns:
            Dictionary with tokens and metadata
        Raises:
            SpotifyOAuthError: For invalid codes
        """
        token_info = self.oauth.get_access_token(code)
        token_info.setdefault('scope', '')
        
        return TokenResponse(
            access_token=token_info["access_token"],
            refresh_token=token_info["refresh_token"],
            token_type=token_info["token_type"],
            expires_in=token_info["expires_in"],
            
        )
    
    def get_user_info(self, access_token: str) -> Dict:
        """
        Get current user's profile information
        Args:
            access_token: Valid Spotify access token
        Returns:
            Dictionary with user profile
        Raises:
            SpotifyAPIError: For API failures
        """
        sp = spotipy.Spotify(auth=access_token)
        return sp.current_user()
    