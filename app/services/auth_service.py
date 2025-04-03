from app.services.spotify_service import SpotifyService
from app.repositories.user_repository import UserRepository
from app.repositories.spotify_repository import SpotifyRepository

class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        spotify_repo: SpotifyRepository,
        spotify_service: SpotifyService
    ):
        self.user_repo = user_repo
        self.spotify_repo = spotify_repo
        self.spotify_service = spotify_service
    
    def handle_spotify_callback(self, code: str) -> dict:
        """
        Complete Spotify OAuth flow:
        1. Exchange code for tokens
        2. Get user profile
        3. Create/update local user
        4. Store credentials
        
        Args:
            code: Spotify OAuth authorization code
            
        Returns:
            Dictionary with:
            - tokens: Spotify tokens
            - user_info: Basic user data
            
        Raises:
            ValueError: For invalid OAuth codes
            AuthError: For authentication failures
        """
        try:
            # 1. Get tokens from Spotify
            tokens = self.spotify_service.exchange_code_for_tokens(code) 
            # 2. Get user profile           
            user_info = self.spotify_service.get_user_info(tokens.access_token)
            # 3. Create/update user
            user = self.user_repo.get_or_create(                
                email=user_info['email']
            )
            # 4. Store credentials
            self.spotify_repo.create_or_update(
                {
                "user_id":user.id,
                "spotify_user_id":user_info['id'],
                "access_token":tokens.access_token,
                "refresh_token":tokens.refresh_token,
                "expires_in":tokens.expires_in
                }
            )
            
            return {
                "tokens": tokens,
                "user_info": {
                    "id": user.id,
                    "email": user.email,
                    "spotify_id": user_info['id']
                }
            }
            
        except KeyError as e:
            raise ValueError(f"Missing expected field in Spotify response: {str(e)}")