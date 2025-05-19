from backend.extensions import db

class Wishlist(db.Model):
    __tablename__ = "wishlist"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    
    # Define relationships
    user = db.relationship("User", backref=db.backref("wishlist_items", lazy=True))
    product = db.relationship("Product", backref=db.backref("wishlist_entries", lazy=True))
    
    def __repr__(self):
        return f"<Wishlist user_id={self.user_id}, product_id={self.product_id}>"