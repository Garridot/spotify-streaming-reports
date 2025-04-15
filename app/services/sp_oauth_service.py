import spotipy
import os
from spotipy.oauth2 import SpotifyOAuth
from app.core.config import Config
from app.models.schemas.spotify import TokenResponse
from app.services.auth_service import AuthService
from app.services.spotify_service import SpotifyService
from app.repositories.spotify_repository import SpotifyRepository
from app.core.security import jwt_manager
from app.core.database import db
from datetime import datetime

class SPOAuthService:

    def __init__(self):       
        self.sp_oauth = SpotifyOAuth(            
            client_id=Config.SPOTIFY_CLIENT_ID,
            client_secret=Config.SPOTIFY_CLIENT_SECRET,
            redirect_uri=Config.SPOTIFY_REDIRECT_URI,
            scope="user-read-email user-read-private user-top-read user-read-recently-played",  
        )  
        self.auth_service = AuthService
        self.spotify_service = SpotifyService
        self.spotify_repo = SpotifyRepository(db.session)   


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
    
    def refresh_access_token(self, user_id: int, refresh_token: str) -> dict:
        """
        Refreshes an expired access token using the refresh token
        Arguments:
            refresh_token (str): Valid refresh token
        Returns:
            dict: new access token:               
        """
        data = self.sp_oauth.refresh_access_token(refresh_token)    
        
        self.spotify_repo.create_or_update({
            "user_id": user_id,            
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "expires_in": data["expires_in"]
        })   
        return data["access_token"]
        

    def handle_spotify_callback(self, code: str) -> dict:
        """
        Complete Spotify OAuth flow
        - Create/update user
        - Get token from Spotify
        - Store credentials
        Arguments:
            code (str): token received from Spotify
        Returns:
            dict: access and refresh tokens of the user
        """
        # 1. Get tokens from Spotify
        tokens = self.sp_oauth.exchange_code_for_tokens(code)
        
        # 2. Get user info
        user_info = self.spotify_service.get_user_info(tokens.access_token)
        
        # 3. Create/update user
        user = self.auth_service.create_or_update_user(user_info['email'])        
        
        # 4. Store credentials
        self.spotify_repo.create_or_update({
            "user_id": user.id,
            "spotify_user_id": user_info['id'],
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "expires_in": tokens.expires_in
        })

        access_token = jwt_manager.create_access_token(user.id)
        refresh_token = jwt_manager.create_refresh_token(user.id)       
        
        return {
            "user": user.email,
            "tokens": {
                "access": access_token,
                "refresh": refresh_token
            }
        }

    def is_token_expired(self, user_id) -> bool:
        """
        Check if the Spotify access token of the user has expired
        Arguments:
            user_id (int)
        """
        user = self.spotify_repo.get_by_user_id(user_id)      
        return datetime.utcnow() >= user.token_expires_at    
