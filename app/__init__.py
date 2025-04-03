from flask import Flask
from .core.database import db
from .dependencies import DIContainer
from flask_migrate import Migrate

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.core.config.Config')
    
    db.init_app(app)
    migrate.init_app(app, db)    
    
    with app.app_context():
        app.container = DIContainer(db)
    
    from .api import register_blueprints
    register_blueprints(app)
    
    return app