from flask import Flask
from flask_login import LoginManager
from backend.config.config import Config
from backend.extensions import db
from backend.models import User
from backend import create_app

app = create_app()

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

if __name__ == "__main__":
    with app.app_context():
        print("Database URI:", app.config["SQLALCHEMY_DATABASE_URI"])
    app.run(debug=True)

# mahmoud