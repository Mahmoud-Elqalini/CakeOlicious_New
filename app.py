from flask_login import LoginManager
from backend.models import User
from backend.routes.auth import auth_bp
from backend.routes.products import product_bp
from backend.routes.cart import cart_bp
from backend.routes.checkout import checkout_bp
from backend.routes.orders import order_bp
from backend.routes.admin import admin_bp
from backend import create_app
from flask_cors import CORS


app = create_app()
CORS(app)


# Flask-Login configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"  

# Function to load user
@login_manager.user_loader
def load_user(user_id):
    from backend.extensions import db
    return db.session.get(User, int(user_id))

@app.route("/")
def home():
    return "Hello, World!"

# Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(product_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(checkout_bp)
app.register_blueprint(order_bp)
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    with app.app_context():
        print("✅ Database URI:", app.config["SQLALCHEMY_DATABASE_URI"])
    app.run(debug=True)
