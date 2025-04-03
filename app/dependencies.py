from app.repositories.user_repository import UserRepository
from app.repositories.spotify_repository import SpotifyRepository
from app.services.spotify_service import SpotifyService
from app.services.auth_service import AuthService

class DIContainer:
    def __init__(self, db):
        self._db = db
        self._services = {}

    @property
    def db_session(self):
        return self._db.session

    def get_service(self, service_class):
        """Factory centralizada para todos los servicios"""
        if service_class not in self._services:
            if service_class == SpotifyService:
                self._services[service_class] = SpotifyService()
            elif service_class == AuthService:
                self._services[service_class] = AuthService(
                    user_repo=UserRepository(self.db_session),
                    spotify_repo=SpotifyRepository(self.db_session),
                    spotify_service=self.get_service(SpotifyService)
                )
        return self._services[service_class]

    @property
    def spotify_service(self):
        return self.get_service(SpotifyService)

    @property
    def auth_service(self):
        return self.get_service(AuthService)