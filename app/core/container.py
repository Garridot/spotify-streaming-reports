from app.services.auth_service import AuthService
from app.services.spotify_service import SpotifyService
from app.services.sp_oauth_service import SPOAuthService
from app.services.fm_oauth_service import FMOAuthService
from app.services.lastfm_service import LastfmService
from app.repositories.user_repository import UserRepository
from app.repositories.spotify_repository import SpotifyRepository
from app.repositories.lastfm_repository import LastfmRepository
from app.repositories.daily_register_repository import DailyTracksPlayedRepository
from app.repositories.weekly_register_repository import WeeklyTracksPlayedRepository
from app.core.database import db

class Container:
    def __init__(self, app):
        self.app = app
        self._init_repositories()
        self._init_services()
    
    def _init_repositories(self):
        self.user_repository = UserRepository(db.session)
        self.spotify_repository = SpotifyRepository(db.session)
        self.lastfm_rerpository = LastfmRepository(db.session)
        self.daily_register_repository = DailyTracksPlayedRepository(db.session)
        self.weekly_register_repository = WeeklyTracksPlayedRepository(db.session) 
    
    def _init_services(self):
        self.auth_service = AuthService(self.user_repository)
        self.spotify_service = SpotifyService()
        self.lastfm_service = LastfmService()
        self.sp_oauth_service = SPOAuthService()
        self.fm_oauth_service = FMOAuthService(
            auth_service=self.auth_service,
            lastfm_service=self.lastfm_service,
            lastfm_rerpository=self.lastfm_rerpository
        )