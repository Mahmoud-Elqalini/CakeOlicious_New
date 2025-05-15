from backend.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    pass_word = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    user_address = db.Column(db.Text)
    phone_number = db.Column(db.String(20))
    user_role = db.Column(db.String(20), nullable=False)

    
    __table_args__ = (
        db.CheckConstraint(
            "user_role IN ('Admin', 'Customer')", name="check_user_role"
        ),
    )

    
    orders = db.relationship("Order", backref="user", lazy=True)
    reviews = db.relationship("ProductReview", backref="reviewer", lazy=True)

    
    def set_password(self, password):
        self.pass_word = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pass_word, password)

    
    @property
    def is_admin(self):
        return self.user_role == "Admin"
