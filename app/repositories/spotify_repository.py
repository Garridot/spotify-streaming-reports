from sqlalchemy.orm import Session
from app.models.domain.spotify import SpotifyAccount
from app.models.schemas.spotify import SpotifyAccountCreate
from datetime import datetime, timedelta

class SpotifyRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: str) -> SpotifyAccount:
        """Retrieves Spotify credentials by internal user ID"""
        return self.db.query(SpotifyAccount).filter(SpotifyAccount.user_id == user_id).first()

    def create_or_update(self, account_data: dict) -> SpotifyAccount:  
        """
        Upserts Spotify account credentials
        Args:
            user_id: Internal user ID
            spotify_user_id: User's Spotify ID
            access_token: OAuth access token
            refresh_token: OAuth refresh token 
            expires_in: Token lifetime in seconds
        Returns:
            Updated SpotifyAccount entity
        """            
        account = self.get_by_user_id(account_data["user_id"])   
        expires_at = datetime.utcnow() + timedelta(seconds=account_data["expires_in"])           
        if account:
            # Update existing             
            account.access_token = account_data["access_token"]
            account.refresh_token = account_data["refresh_token"]
            account.token_expires_at = expires_at
        else:
            # Create new
            account = SpotifyAccount(
                user_id=account_data["user_id"],
                spotify_user_id=account_data["spotify_user_id"],
                spotify_username=account_data["spotify_username"],
                profile_image_url=account_data["profile_image_url"],
                access_token=account_data["access_token"],
                refresh_token=account_data["refresh_token"],
                token_expires_at=expires_at
            )
            self.db.add(account)
        
        self.db.commit()
        self.db.refresh(account)
        return account
