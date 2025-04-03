from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SpotifyAccountBase(BaseModel):
    """Shared Spotify account properties"""
    spotify_user_id: str
    access_token: str
    refresh_token: str
    token_expires_at: datetime

class SpotifyAccountCreate(SpotifyAccountBase):
    """Properties to receive on creation"""
    user_id: str

class SpotifyAccountOut(SpotifyAccountBase):
    """Properties to return to client"""
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):    
    """Standard OAuth2 token response"""    
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: Optional[str] = Field(default="")  
    expires_at: Optional[datetime] = None  

    @classmethod
    def from_spotify_response(cls, token_info: dict):
        """Método factory para crear desde la respuesta de Spotify"""
        return cls(
            access_token=token_info['access_token'],
            token_type=token_info['token_type'],
            expires_in=token_info['expires_in'],
            refresh_token=token_info['refresh_token'],
            scope=token_info.get('scope', ''),
            expires_at=datetime.utcnow() + timedelta(seconds=token_info['expires_in'])
        )

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "NgCXRK...MzYjw",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "NgAagA...Um_SHo",
                "scope": "user-read-email",
                "expires_at": "2025-04-02T20:16:53.514Z"
            }
        }