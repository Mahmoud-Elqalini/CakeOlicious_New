from backend import create_app
from backend.extensions import db
from backend.models.User import User
from backend.models.Category import Category
from backend.models.Product import Product
from werkzeug.security import generate_password_hash

def init_db():
    app = create_app()
    
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        # Create admin user
        admin = User(
            username="admin",
            email="admin@example.com",
            full_name="Admin User",
            user_role="Admin"
        )
        admin.set_password("admin123")
        
        # Create categories
        categories = [
            Category(category_name="Cakes", description="Delicious cakes for all occasions"),
            Category(category_name="Cookies", description="Freshly baked cookies"),
            Category(category_name="Pastries", description="Flaky and delicious pastries"),
            Category(category_name="Breads", description="Freshly baked breads")
        ]
        
        # Create products
        products = [
            Product(
                product_name="Chocolate Cake",
                description="Rich chocolate cake with chocolate frosting",
                price=25.99,
                stock=10,
                image_url="/uploads/chocolate_cake.jpg",
                category_id=1,
                discount=0
            ),
            Product(
                product_name="Vanilla Cake",
                description="Light and fluffy vanilla cake with vanilla frosting",
                price=22.99,
                stock=15,
                image_url="/uploads/vanilla_cake.jpg",
                category_id=1,
                discount=5
            ),
            Product(
                product_name="Chocolate Chip Cookies",
                description="Classic chocolate chip cookies",
                price=12.99,
                stock=20,
                image_url="/uploads/chocolate_chip_cookies.jpg",
                category_id=2,
                discount=0
            ),
            Product(
                product_name="Croissant",
                description="Flaky and buttery croissants",
                price=3.99,
                stock=30,
                image_url="/uploads/croissant.jpg",
                category_id=3,
                discount=0
            ),
            Product(
                product_name="Sourdough Bread",
                description="Artisanal sourdough bread",
                price=6.99,
                stock=25,
                image_url="/uploads/sourdough_bread.jpg",
                category_id=4,
                discount=0
            )
        ]
        
        # Add all to database
        db.session.add(admin)
        db.session.add_all(categories)
        db.session.add_all(products)
        
        # Commit changes
        db.session.commit()
        
        print("Database initialized with sample data!")

if __name__ == "__main__":
    init_db()