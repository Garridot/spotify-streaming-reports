from flask import Flask
from .core.database import db
from flask_migrate import Migrate
from .core.security import jwt_manager 
from app.core.config import Config
from app.core.container import Container
from .api import register_blueprints

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.core.config.Config')
    
    db.init_app(app)
    migrate.init_app(app, db)  

    app.config['SECRET_KEY'] = Config.SECRET_KEY     

    jwt_manager.init_app(app)   

    app.container = Container(app)
    register_blueprints(app)
    
    return app