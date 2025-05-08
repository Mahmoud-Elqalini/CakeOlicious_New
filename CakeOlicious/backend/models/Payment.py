from backend.extensions import db
from datetime import datetime

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    
    # CHECK RESTRICTIONS
    __table_args__ = (
        db.CheckConstraint("payment_method IN ('Credit Card', 'PayPal', 'Bank Transfer', 'Cash on Delivery', 'Gift Card')", name='check_payment_method'),
        db.CheckConstraint("status IN ('Pending', 'Completed')", name='check_payment_status'),
    )
    
    