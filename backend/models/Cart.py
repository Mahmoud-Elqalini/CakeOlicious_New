from backend.extensions import db
from datetime import datetime

class Cart(db.Model):
    __tablename__ = 'cart'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    is_checked_out = db.Column(db.Boolean, default=False)

    # Relationships
    user = db.relationship('User', backref='carts', lazy=True)
    cart_details = db.relationship('CartDetails', backref='cart', lazy=True)