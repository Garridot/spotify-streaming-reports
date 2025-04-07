import os
from typing import Dict, Optional
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from app.core.config import Config
from app.models.schemas.spotify import TokenResponse
from app.services.auth_service import AuthService
from app.repositories.spotify_repository import SpotifyRepository

class SpotifyService:
    def __init__(self):       
        self.sp_oauth = SpotifyOAuth(
            client_id=Config.SPOTIFY_CLIENT_ID,
            client_secret=Config.SPOTIFY_CLIENT_SECRET,
            redirect_uri=Config.SPOTIFY_REDIRECT_URI,
            scope="user-read-email user-read-private user-top-read user-read-recently-played",  
        )

    def get_oauth_url(self) -> str:
        """Generate Spotify authorization URL"""
        return self.sp_oauth.get_authorize_url()
    
    def exchange_code_for_tokens(self, code: str) -> TokenResponse:
        """Exchange authorization code for tokens"""
        token_info = self.sp_oauth.get_access_token(code)
        return TokenResponse(
            access_token=token_info["access_token"],
            refresh_token=token_info["refresh_token"],
            token_type=token_info["token_type"],
            expires_in=token_info["expires_in"],
            scope=token_info.get("scope", "")
        )
    
    def get_user_info(self, access_token: str) -> dict:
        """Get current user's profile info"""
        sp = spotipy.Spotify(auth=access_token)
        return sp.current_user()    
    
   