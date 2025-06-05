from flask import Flask
from .core.database import db
from flask_migrate import Migrate
from .core.security import jwt_manager 
from app.core.config import config, Config
from app.core.container import Container
from .api import register_blueprints
import os

migrate = Migrate()

def create_app():
    app = Flask(__name__)

    template_path = os.path.join(os.path.dirname(__file__), 'templates')
    
    app = Flask(__name__,
               template_folder=template_path,
               static_folder='static')           

    config_name = os.getenv("FLASK_ENV")

    app.config.from_object(config[config_name])    
    
    db.init_app(app)
    migrate.init_app(app, db)  

    app.config['SECRET_KEY'] = Config.SECRET_KEY     

    jwt_manager.init_app(app)   

    app.container = Container(app)
    register_blueprints(app)        
    
    return app