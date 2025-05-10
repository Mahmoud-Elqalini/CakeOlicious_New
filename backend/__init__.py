from flask import Flask
from flask_migrate import Migrate
from backend.extensions import db
from backend.routes.auth import auth_bp
from backend.routes.orders import order_bp
from backend.routes.products import product_bp
from backend.routes.cart import cart_bp
from backend.routes.payments import payment_bp
# from backend.routes.reviews import review_bp
from backend.routes.checkout import checkout_bp
from backend.routes.admin import admin_bp
from flask_cors import CORS

def create_app():

    # Create a Flask app with templates and static locating
    app = Flask(__name__, 
                template_folder="../frontend/templates", 
                static_folder="../frontend/static")
    
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Download settings from config.py
    app.config.from_object('backend.config.config')
    
    # Link SQLAlchemy to the app
    db.init_app(app)
    
    # Set up Flask-Migrate to manage database changes
    Migrate(app, db)
    
    # Blueprints Registration
    app.register_blueprint(auth_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(payment_bp)
    # app.register_blueprint(review_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(admin_bp)
    
    # Create tables in the database
    with app.app_context():
        db.create_all()
    
    return app
