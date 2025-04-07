from app.repositories.user_repository import UserRepository
from app.core.database import db

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repo = user_repository 

    def get_user_by_id(self,id):
        user = self.get_user_by_id(id)
        return user
        
    def create_or_update_user(self, email):
        """Create / update user"""        
        user = self.user_repo.get_or_create(email=email) 
        return user
    
    