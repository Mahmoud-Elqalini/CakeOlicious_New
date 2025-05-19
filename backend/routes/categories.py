from flask import Blueprint, jsonify, request
from backend.extensions import db
from backend.models.Category import Category
from backend.routes.auth import token_required  # Ensure correct import
from sqlalchemy.sql import text
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

categories_bp = Blueprint("categories", __name__)

@categories_bp.route('/categories', methods=['GET'])
def get_categories():
    try:
        # Use direct SQL query to get categories with proper column names
        categories_query = text("SELECT id, category_name FROM categories")
        result = db.session.execute(categories_query).fetchall()
        
        # Debug the raw result
        logger.debug(f"Raw categories query result: {result}")
        
        formatted_categories = []
        for row in result:
            # Debug each row
            logger.debug(f"Category row: {row}")
            category = {
                'id': row.id,
                'category_name': row.category_name  # Make sure this matches the column name in your database
            }
            formatted_categories.append(category)
            
        logger.info(f"Formatted categories: {formatted_categories}")
        return jsonify({'categories': formatted_categories}), 200
    except Exception as e:
        logger.error(f"Error retrieving categories: {str(e)}")
        return jsonify({'error': str(e)}), 500

@categories_bp.route('/categories/<int:category_id>/products', methods=['GET'])
def get_category_products(category_id):
    try:
        # Pagination parameters
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        
        # Get category name
        category = Category.query.get_or_404(category_id)
        
        # Get products for this category
        products_query = text("""
            SELECT p.id, p.product_name, p.description, p.price, p.stock, 
                   p.image_url, p.discount, p.is_active
            FROM products p
            WHERE p.category_id = :category_id AND p.is_active = 1
            ORDER BY p.id
            OFFSET :offset ROWS
            FETCH NEXT :limit ROWS ONLY
        """)
        
        offset = (page - 1) * per_page
        result = db.session.execute(
            products_query, 
            {"category_id": category_id, "offset": offset, "limit": per_page}
        ).fetchall()
        
        # Count total products
        count_query = text("""
            SELECT COUNT(*) as total
            FROM products
            WHERE category_id = :category_id AND is_active = 1
        """)
        count_result = db.session.execute(count_query, {"category_id": category_id}).fetchone()
        total = count_result.total if count_result else 0
        
        # Format products
        products = []
        for row in result:
            product = {
                'id': row.id,
                'product_name': row.product_name,
                'description': row.description,
                'price': float(row.price),
                'stock': row.stock,
                'image_url': row.image_url,
                'discount': float(row.discount or 0),
                'is_active': row.is_active
            }
            products.append(product)
        
        return jsonify({
            'category': {
                'id': category.id,
                'name': category.category_name
            },
            'products': products,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving category products: {str(e)}")
        return jsonify({'error': str(e)}), 500

@categories_bp.route('/categories', methods=['POST'])
@token_required
def create_category(current_user):
    # Check if user is admin
    if current_user.user_role.lower() != 'admin':
        return jsonify({'message': 'Unauthorized'}), 403
        
    data = request.get_json()
    category_name = data.get('category_name')
    
    if not category_name:
        return jsonify({'message': 'Category name is required'}), 400
        
    try:
        # Check if category already exists
        existing = Category.query.filter_by(category_name=category_name).first()
        if existing:
            return jsonify({'message': 'Category already exists'}), 400
            
        # Create new category
        new_category = Category(category_name=category_name)
        db.session.add(new_category)
        db.session.commit()
        
        return jsonify({
            'message': 'Category created successfully',
            'category': {
                'id': new_category.id,
                'name': new_category.category_name
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating category: {str(e)}")
        return jsonify({'message': f'Error: {str(e)}'}), 500
