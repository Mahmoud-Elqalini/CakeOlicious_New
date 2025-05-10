from flask import Flask
from flask_login import LoginManager
from backend.config.config import Config
from backend.extensions import db
from backend.models import User
from backend.routes.auth import auth_bp
from backend.routes.products import product_bp
from backend.routes.cart import cart_bp
from backend.routes.checkout import checkout_bp
from backend.routes.orders import order_bp
from backend.routes.admin import admin_bp
import os
from backend import create_app

# from backend.routes.reviews import review_bp

# app = Flask(
#     __name__, template_folder="frontend/templates", static_folder="frontend/static"
# )

app=create_app();

# Download settings from Config
app.config.from_object(Config)

# Initializing SQLAalchemy with the application
db.init_app(app)

# Flask-Login configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = (
    "auth.login"  # We set the login page (we will do it in auth_bp)
)


# Function to load user (required for Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    return "Hello, World!"


# Blueprints Registration
app.register_blueprint(auth_bp)
app.register_blueprint(product_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(checkout_bp)
app.register_blueprint(order_bp)
app.register_blueprint(admin_bp)
# app.register_blueprint(review_bp)

if __name__ == "__main__":
    with app.app_context():
        # print("Environment variables:")
        # print(f"FLASK_ENV: {os.getenv('FLASK_ENV')}")
        # print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
        # print(f"Config DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        # This line is not necessary because we use Stored Procedures with SQL Server
        # db.create_all()
        print(
            "Database URI:", app.config["SQLALCHEMY_DATABASE_URI"]
        )  # To make sure the setting is loaded
    app.run(debug=True)
