import logging
from app.core.config import Config
from app.workers.daily_task import sync_all_users_daily_register
from app.core.database import init_db
from app import create_app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():       
        sync_all_users_daily_register()