from app.tasks.weekly_task import sync_all_users_weekly_register
from flask import current_app
from app import create_app
import pandas as pd
import json

if __name__ == '__main__': 
    app = create_app()
    with app.app_context():
        sync_all_users_weekly_register()