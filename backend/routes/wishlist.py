from flask import Blueprint, jsonify, request
from backend.extensions import db
from backend.models.User import User
from backend.models.Product import Product
from backend.models.Wishlist import Wishlist  # Import the Wishlist model
from backend.routes.auth import token_required
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

wishlist_bp = Blueprint("wishlist", __name__)

@wishlist_bp.route('/wishlist', methods=['GET'])
@token_required
def get_wishlist(current_user):
    try:
        logger.debug(f"Retrieving wishlist for user {current_user.id}")
        
        # Use the ORM instead of raw SQL for better error handling
        wishlist_items = db.session.query(
            Product.id,
            Product.product_name,
            Product.product_description.label('description'),  # Use the correct column name
            Product.price,
            Product.image_url,
            Product.discount
        ).join(
            Wishlist, Wishlist.product_id == Product.id
        ).filter(
            Wishlist.user_id == current_user.id
        ).all()
        
        formatted_items = []
        for item in wishlist_items:
            formatted_items.append({
                "id": item.id,
                "product_name": item.product_name,
                "description": item.description,
                "price": float(item.price) if item.price else 0,
                "image_url": item.image_url,
                "discount": float(item.discount) if item.discount else 0
            })
        
        logger.info(f"Retrieved {len(formatted_items)} wishlist items for user {current_user.id}")
        return jsonify({
            "success": True,
            "message": "Wishlist retrieved successfully",
            "data": formatted_items
        }), 200
            
    except Exception as e:
        logger.error(f"Error retrieving wishlist: {str(e)}")
        return jsonify({
            "success": False, 
            "message": "Error retrieving wishlist", 
            "error": str(e)
        }), 500

@wishlist_bp.route('/wishlist/add', methods=['POST'])
@token_required
def add_to_wishlist(current_user):
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        
        logger.debug(f"Adding product {product_id} to wishlist for user {current_user.id}")
        
        if not product_id:
            logger.warning("Product ID is required but was not provided")
            return jsonify({
                "success": False,
                "message": "Product ID is required"
            }), 400
            
        # Check if product exists
        product = Product.query.get(product_id)
        if not product:
            logger.warning(f"Product with ID {product_id} not found")
            return jsonify({
                "success": False,
                "message": "Product not found"
            }), 404
            
        # Check if already in wishlist using ORM
        existing_item = Wishlist.query.filter_by(
            user_id=current_user.id, 
            product_id=product_id
        ).first()
        
        if existing_item:
            logger.info(f"Product {product_id} already in wishlist for user {current_user.id}")
            return jsonify({
                "success": False,
                "message": "Product already in wishlist"
            }), 400
            
        # Add to wishlist using ORM
        new_wishlist_item = Wishlist(
            user_id=current_user.id,
            product_id=product_id
        )
        
        db.session.add(new_wishlist_item)
        db.session.commit()
        
        logger.info(f"Product {product_id} added to wishlist for user {current_user.id}")
        return jsonify({
            "success": True,
            "message": "Product added to wishlist"
        }), 201
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding to wishlist: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error adding to wishlist",
            "error": str(e)
        }), 500

@wishlist_bp.route('/wishlist/remove', methods=['POST'])
@token_required
def remove_from_wishlist_post(current_user):
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        
        logger.debug(f"Removing product {product_id} from wishlist for user {current_user.id}")
        
        if not product_id:
            logger.warning("Product ID is required but was not provided")
            return jsonify({
                "success": False,
                "message": "Product ID is required"
            }), 400
            
        # Remove from wishlist using ORM
        deleted = Wishlist.query.filter_by(
            user_id=current_user.id, 
            product_id=product_id
        ).delete()
        
        if deleted == 0:
            logger.warning(f"Product {product_id} not found in wishlist for user {current_user.id}")
            return jsonify({
                "success": False,
                "message": "Product not found in wishlist"
            }), 404
            
        db.session.commit()
        
        logger.info(f"Product {product_id} removed from wishlist for user {current_user.id}")
        return jsonify({
            "success": True,
            "message": "Product removed from wishlist"
        }), 200
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error removing from wishlist: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error removing from wishlist",
            "error": str(e)
        }), 500



