from backend.extensions import db
from datetime import datetime

class CartDetails(db.Model):
    __tablename__ = 'cart_details'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    discount = db.Column(db.Numeric(5, 2), default=0.0)
    added_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)

    # Constraints
    __table_args__ = (
        db.CheckConstraint('quantity > 0', name='check_quantity_positive'),
        db.UniqueConstraint('cart_id', 'product_id', name='UQ_Cart_Product'),
    )

    # Relationships
    product = db.relationship('Product', backref='cart_details', lazy=True)