from backend.extensions import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    discount = db.Column(db.Float, default=0)
    is_active = db.Column(db.Boolean, default=True)

    
    category = db.relationship("Category", backref="products")

    def __repr__(self):
        return f"<Product {self.product_name}>"
