from flask import Flask, render_template, request, jsonify, redirect, make_response
from .core.database import db
from flask_migrate import Migrate
from .core.security import jwt_manager, token_required 
from app.core.config import config, Config
from app.core.container import Container
from .api import register_blueprints
import os
import jwt
from functools import wraps

migrate = Migrate()

def anonymous_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('x-access-token') or request.cookies.get('x-access_token')
        if token:
            try:
                jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
                return redirect("/home")
            except jwt.ExpiredSignatureError:
                pass
            except jwt.InvalidTokenError:
                pass
        return f(*args, **kwargs)
    return decorated_function   

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

    @app.route("/")
    @anonymous_only
    def login():
        return render_template("login.html")

    @app.route("/logout")    
    def logout():
        response = make_response(redirect("http://127.0.0.1:8000/"))
        response.delete_cookie('x-access_token')
        response.delete_cookie('x-refresh_token')
        return response 

    @app.route("/home")
    @token_required
    def home(current_user):          
        return render_template("home.html")    

    
    return app