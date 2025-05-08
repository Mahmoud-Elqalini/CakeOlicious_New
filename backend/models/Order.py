from backend.extensions import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    shipping_address = db.Column(db.String(255), nullable=False)  # Adding the ShippingAddress column
    status = db.Column(db.String(20), nullable=False)
    
    # CHECK constraint for status
    __table_args__ = (
        db.CheckConstraint("status IN ('Pending', 'Shipped', 'Delivered')", name='check_status'),
    )
    
    # Relationships
    order_details = db.relationship('OrderDetail', backref='order', lazy=True)
    payment = db.relationship('Payment', backref='order', uselist=False)

