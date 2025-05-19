from flask import Flask, send_from_directory
from flask_migrate import Migrate
from backend.extensions import db
from backend.routes.auth import auth_bp
from backend.routes.orders import order_bp
from backend.routes.products import product_bp
from backend.routes.cart import cart_bp
from backend.routes.payments import payment_bp
from backend.routes.checkout import checkout_bp
from backend.routes.admin import admin_bp
from backend.routes.uploads import upload_bp
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__, 
                template_folder="../frontend/templates", 
                static_folder="static")
    
    os.makedirs(os.path.join(app.root_path, 'uploads'), exist_ok=True)
    os.makedirs(os.path.join(app.root_path, 'static', 'uploads'), exist_ok=True)

    @app.route('/static/<path:filename>')
    def serve_static(filename):
        return send_from_directory(os.path.join(app.root_path, 'static'), filename)
    
    # Update CORS configuration to include both localhost:5174 and 127.0.0.1:5174
    CORS(app, 
         origins=["http://localhost:5174", "http://127.0.0.1:5174", "http://localhost:3000"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         supports_credentials=True,
         max_age=3600)
    
    @app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
    @app.route('/<path:path>', methods=['OPTIONS'])
    def handle_options(path):
        return '', 200
    
    app.config.from_object('backend.config.config')
    
    db.init_app(app)
    
    Migrate(app, db)
    
    
    
    with app.app_context():
        db.create_all()
    
    return app
