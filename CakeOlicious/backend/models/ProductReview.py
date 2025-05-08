from backend.extensions import db
from datetime import datetime

class ProductReview(db.Model):
    __tablename__ = 'product_reviews'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rating = db.Column(db.Integer)
    review_text = db.Column(db.Text)
    review_date = db.Column(db.DateTime, default=datetime.utcnow)
    
   # CHECK constraint for rating
    __table_args__ = (
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating'),
    )
    
    # Relationships
    product = db.relationship('Product', backref='reviews')

    