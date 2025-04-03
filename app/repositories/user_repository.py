from sqlalchemy.orm import Session
from app.models.domain.user import User
from app.models.schemas.user import UserCreate

class UserRepository:
    def __init__(self, db_session):
        self.db = db_session

    def get_by_email(self, email: str):
        """Finds user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_spotify_id(self, spotify_id: str):
        """Retrieves a user by primary key"""
        return self.db.query(User).filter(User.spotify_id == spotify_id).first()

    def create(self, email: str, spotify_id: str = None):
        """
        Creates new user with autogenerated ID
        Args:
            email: User's email address (unique)
            spotify_id: Optional Spotify ID for association
        Returns:
            Persisted User entity
        """
        user = User(email=email, spotify_id=spotify_id)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)  
        return user

    def get_or_create(self, email: str, spotify_id: str = None):
        """
        Atomic get-or-create operation
        Returns existing user if found, otherwise creates new
        """
        user = self.get_by_email(email) or self.get_by_spotify_id(spotify_id)
        if not user:
            user = self.create(email, spotify_id)
        elif spotify_id and not user.spotify_id:
            # Actualizar spotify_id si no estaba guardado
            user.spotify_id = spotify_id
            self.db.commit()
        return user