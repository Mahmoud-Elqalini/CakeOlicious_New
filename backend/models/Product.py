from backend.extensions import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    product_description = db.Column(db.Text, nullable=True)  # Changed from description to product_description
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    discount = db.Column(db.Float, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    # Removed created_at and updated_at as they don't exist in the database
    
    # Relationships
    category = db.relationship('Category', backref=db.backref('products', lazy=True))
    
    def __repr__(self):
        return f'<Product {self.product_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'description': self.product_description,  # Keep the API consistent
            'price': float(self.price),
            'stock': self.stock,
            'category_id': self.category_id,
            'image_url': self.image_url,
            'discount': float(self.discount),
            'is_active': self.is_active
        }
