from flask import Blueprint, jsonify
from sqlalchemy import text
from backend.extensions import db  # Changed from backend.models.db
import logging

logger = logging.getLogger(__name__)

bestsellers_bp = Blueprint('bestsellers', __name__)

@bestsellers_bp.route('/bestsellers', methods=['GET'])
def get_bestsellers():
    try:
        logger.info("Bestsellers endpoint called")
        
        # First, check if we can execute a simple query to verify connection
        test_query = text("SELECT 1 AS test")
        test_result = db.session.execute(test_query).fetchone()
        logger.info(f"Test query result: {test_result}")
        
        # Get the column names from the database schema
        schema_query = text("""
            SELECT TOP 1 * FROM products
        """)
        schema_result = db.session.execute(schema_query).fetchone()
        logger.info(f"Available columns: {schema_result.keys()}")
        
        # Use a simpler approach - get the most recent products
        # Updated column names based on your database schema
        products_query = text("""
            SELECT TOP 8 p.id, p.product_name, p.product_description, p.price, 
                   ISNULL(p.discount, 0) as discount, 
                   p.stock, p.image_url, 
                   p.category_id, c.category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.is_active = 1
            ORDER BY p.id DESC
        """)
        
        products_result = db.session.execute(products_query).fetchall()
        
        products = []
        for product in products_result:
            products.append({
                'id': product[0],
                'name': product[1],
                'description': product[2],
                'price': float(product[3]),
                'discount_percentage': float(product[4]),
                'stock_quantity': product[5],
                'image_url': product[6],
                'category_id': product[7],
                'category_name': product[8]
            })
        
        logger.info(f"Returning {len(products)} bestseller products")
        return jsonify({'products': products}), 200
        
    except Exception as e:
        logger.error(f"Error in bestsellers endpoint: {str(e)}")
        # Return a more graceful error with empty products instead of 500
        return jsonify({
            'message': 'Failed to fetch bestsellers',
            'error': str(e),
            'products': []
        }), 200  # Return 200 with empty products instead of 500





