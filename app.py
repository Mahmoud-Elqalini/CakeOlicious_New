from flask import Flask, jsonify
from flask_login import LoginManager
from backend.config.config import Config
from backend.extensions import db
from backend.models import User
from backend.models.Wishlist import Wishlist  # Import the new model
from backend.routes.auth import auth_bp
from backend.routes.products import product_bp
from backend.routes.cart import cart_bp
from backend.routes.checkout import checkout_bp
from backend.routes.orders import order_bp
from backend.routes.admin import admin_bp
from backend.routes.wishlist import wishlist_bp
import os
from backend import create_app

app=create_app();

app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    return "Hello, World!"

app.register_blueprint(auth_bp)
app.register_blueprint(product_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(checkout_bp)
app.register_blueprint(order_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(wishlist_bp)

# Add a debug route to list all registered routes
@app.route('/debug/routes')
def list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            "endpoint": rule.endpoint,
            "methods": list(rule.methods),
            "rule": str(rule)
        })
    return jsonify(routes)

if __name__ == "__main__":
    with app.app_context():
        print("Database URI:", app.config["SQLALCHEMY_DATABASE_URI"])
    app.run(debug=True)
