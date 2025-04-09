from app.models.domain.lastfm import LastfmAccount

class LastfmRepository:
    def __init__(self, db_session):
        self.db = db_session

    def get_by_user_id(self, user_id: int) -> LastfmAccount:
        """Retrieves Lastfm Account credentials by internal user ID"""
        return self.db.query(LastfmAccount).filter(LastfmAccount.user_id == user_id).first()    
    
    def save_credentials(self, user_id: int, username: str, session_key: str):
        """Save or update Last.fm credentials"""
        account = self.db.query(LastfmAccount).filter(
            (LastfmAccount.user_id == user_id) |
            (LastfmAccount.lastfm_username == username)
        ).first()

        if account:
            account.lastfm_session_key = session_key
        else:
            account = LastfmAccount(
                user_id=user_id,
                lastfm_username=username,
                lastfm_session_key=session_key
            )
            self.db.add(account)
        
        self.db.commit()
        return account