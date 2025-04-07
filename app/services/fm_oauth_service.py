from app.services.auth_service import AuthService
from app.services.lastfm_service import LastfmService
from app.repositories.lastfm_repository import LastfmRepository

class FMOAuthService:
    def __init__(
            self, 
            auth_service: AuthService,                  
            lastfm_service: LastfmService,
            lastfm_rerpository: LastfmRepository
        ):
        self.auth_service = auth_service
        self.lastfm_service = lastfm_service
        self.lastfm_rerpository = lastfm_rerpository

    def save_credentials(self, session_data, user):
        
        username = session_data['session']['name']
        session_key = session_data['session']['key']
        
        self.lastfm_rerpository.save_credentials(
            user_id=user.id,
            username=username,
            session_key=session_key
        )

        return {
            "user" : user.id,
            "username": user,
            "session_key":session_key 
        }
