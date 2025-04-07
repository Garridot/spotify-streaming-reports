from app.services.auth_service import AuthService
from app.services.spotify_service import SpotifyService
from app.repositories.spotify_repository import SpotifyRepository
from app.core.security import jwt_manager

class SPOAuthService:
    def __init__(self, auth_service: AuthService, 
                 spotify_service: SpotifyService,
                 spotify_repo: SpotifyRepository):
        self.auth_service = auth_service
        self.spotify_service = spotify_service
        self.spotify_repo = spotify_repo

    def handle_spotify_callback(self, code: str) -> dict:
        """Complete Spotify OAuth flow"""
        # 1. Get tokens from Spotify
        tokens = self.spotify_service.exchange_code_for_tokens(code)
        
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
       
