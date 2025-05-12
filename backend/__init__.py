from flask import Flask
from backend.config.config import Config
from backend.extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  
    db.init_app(app)                
    return app
