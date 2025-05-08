from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from backend.routes.auth import token_required
from backend.extensions import db
from backend.models import Cart
from backend.models import CartDetail
from decimal import Decimal
import logging


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/cart/add', methods=['POST'])
@token_required
def add_to_cart(current_user):
    if not request.is_json:
        logger.error("Invalid JSON format in request")
        return jsonify({'message': 'Invalid JSON format'}), 400

    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity')

    if not product_id or not quantity:
        logger.error("Missing product_id or quantity in request")
        return jsonify({'message': 'Product ID and quantity are required'}), 400
    try:
        result = db.session.execute(
            "EXEC AddToCart @UserID=:user_id, @ProductID=:product_id, @Quantity=:quantity",
            {
                "user_id": current_user.id,
                "product_id": product_id,
                "quantity": quantity
            }
        )
        row = result.fetchone()
        message = row[1]

        db.session.commit()
        logger.info(f"Product {product_id} added to cart for user {current_user.id}")
        return jsonify({'message': message})
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"SQLAlchemy error adding to cart for user {current_user.id}: {str(e)}")
        return jsonify({'message': 'Database error', 'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error adding to cart for user {current_user.id}: {str(e)}")
        return jsonify({'message': 'Unexpected error', 'error': str(e)}), 500
    
# #######################################################################################################################################

@cart_bp.route('/cart', methods=['GET'])
@token_required
def view_cart(current_user):

    try:
        # Execute the stored procedure to get cart details for the user
        result = db.session.execute(
            "EXEC GetCartDetails @UserID=:user_id",
            {"user_id": current_user.id}
        )
        cart_items = result.fetchall()
        print(cart_items)
        # If there are no items in the cart or if the result is an error message
        if not cart_items:
            message = cart_items[0][0] if cart_items else "Cart is empty."
            return jsonify({
                "success": False,
                "message": message,
                "data": [],
                "total_price": 0
            }), 400

        # Use total price from SQL (present in every row in position [7])
        total_price = cart_items[0][7]
        total_price = float(total_price) if isinstance(total_price, Decimal) else total_price

        # Format cart items for JSON response
        formatted_cart_items = []
        for row in cart_items:
            formatted_cart_items.append({
                "customer_name": row[0],
                "product_name": row[1],
                "quantity": float(row[2]) if isinstance(row[2], Decimal) else row[2],
                "unit_price": float(row[3]) if isinstance(row[3], Decimal) else row[3],
                "discount": float(row[4]) if isinstance(row[4], Decimal) else row[4],
                "added_date": row[6]
            })
        logger.info(f"Retrieved {len(formatted_cart_items)} cart items for user {current_user.id}")
        return jsonify({
            "success": True,
            "message": "Cart retrieved successfully.",
            "data": formatted_cart_items,
            "total_price": round(total_price, 2)
        }), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"SQLAlchemy error retrieving cart: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Database error while retrieving cart.",
            "error": str(e)
        }), 500

    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error retrieving cart: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An unexpected error occurred while retrieving cart.",
            "error": str(e)
        }), 500

# #######################################################################################################################################
@cart_bp.route('/cart/update', methods=['POST'])
@token_required
def update_cart_item_quantity(current_user):
    if not request.is_json:
        logger.error("Invalid JSON format in request")
        return jsonify({'message': 'Invalid JSON format'}), 400
    
    data = request.get_json()
    cart_item_id = data.get('cart_item_id')
    change = data.get('change')
    if not cart_item_id or change is None:
        logger.error("Missing cart_item_id or change in request")
        return jsonify({'message': 'Cart item ID and change value are required'}), 400

    try:
        # Verify that the cart item belongs to the current user
        cart_check = db.session.execute(
            "SELECT user_id FROM cart WHERE id = :cart_item_id",
            {"cart_item_id": cart_item_id}
        ).fetchone()
        
        if not cart_check or cart_check[0] != current_user.id:
            logger.warning(f"Unauthorized attempt to update cart item {cart_item_id} by user {current_user.id}")
            return jsonify({'message': 'Unauthorized access to cart item'}), 403
        
        result = db.session.execute(
            "EXEC UpdateCartQuantity @CartItemID=:cart_item_id, @Change=:change",
            {
                "cart_item_id": cart_item_id,
                "change": change
            }
        )
        row = result.fetchone()
        db.session.commit()

        status_code = row[0]
        message = row[1]

        if status_code == 0:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400

    except Exception as e:
        db.session.rollback()
        logger.error(f"SQLAlchemy error updating cart item {cart_item_id}: {str(e)}")
        return jsonify({'success': False, 'message': 'Internal server error', 'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error retrieving cart: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An unexpected error occurred while retrieving cart.",
            "error": str(e)
        }), 500

# #######################################################################################################################################
@cart_bp.route('/cart/remove', methods=['POST'])
@token_required
def remove_from_cart(current_user):
    if not request.is_json:
        logger.error("Invalid JSON format in request")
        return jsonify({'message': 'Invalid JSON format'}), 400
    
    try:
        data = request.get_json()
        cart_item_id = data.get('cart_item_id')

        if not cart_item_id:
            logger.error("Missing cart_item_id in request")
            return jsonify({'message': 'Cart item ID is required'}), 400


        # Verify that the cart item belongs to the current user
        cart_check = db.session.execute(
            "SELECT user_id FROM Cart WHERE id = :cart_item_id",
            {"cart_item_id": cart_item_id}
        ).fetchone()
        
        if not cart_check or cart_check[0] != current_user.id:
            logger.warning(f"Unauthorized attempt to remove cart item {cart_item_id} by user {current_user.id}")
            return jsonify({'message': 'Unauthorized access to cart item'}), 403
        
        # Execute the stored procedure to remove the cart item
        result = db.session.execute(
            "EXEC RemoveFromCart @CartItemID=:cart_item_id",
            {"cart_item_id": cart_item_id}
        )
        
        # Fetch the result (status and message)
        status, message = result.fetchone()

        db.session.commit()

        # Check the status and return the appropriate response
        if status == 0:
            logger.info(f"Removed cart item {cart_item_id} for user {current_user.id}")
            return jsonify({'message': message}), 200  # Successfully removed
        else:
            logger.warning(f"Failed to remove cart item {cart_item_id} for user {current_user.id}: {message}")
            return jsonify({'message': message}), 400  # Error in removal
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"SQLAlchemy error removing from cart for user {current_user.id}: {str(e)}")
        return jsonify({'success': False, 'message': 'Database error', 'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error removing from cart for user {current_user.id}: {str(e)}")
        return jsonify({'success': False, 'message': 'Unexpected error', 'error': str(e)}), 500
# #######################################################################################################################################

# mahmoud