from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from backend.routes.auth import token_required  # Ensure correct import
from backend.extensions import db
from backend.models import Cart
from backend.models import CartDetail
from decimal import Decimal
import logging



logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

cart_bp = Blueprint("cart", __name__)


@cart_bp.route("/cart/add", methods=["POST"])
@token_required
def add_to_cart(current_user):
    if not request.is_json:
        logger.error("Invalid JSON format in request")
        return jsonify({"message": "Invalid JSON format"}), 400

    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity")

    if not product_id or not quantity:
        logger.error("Missing product_id or quantity in request")
        return jsonify({"message": "Product ID and quantity are required"}), 400
    try:
        result = db.session.execute(
            "EXEC AddToCart @UserID=:user_id, @ProductID=:product_id, @Quantity=:quantity",
            {
                "user_id": current_user.id,
                "product_id": product_id,
                "quantity": quantity,
            },
        )
        row = result.fetchone()
        status_code = row[0]  # Assuming first column is status code
        message = row[1]      # Assuming second column is message

        db.session.commit()
        logger.info(f"Product {product_id} added to cart for user {current_user.id}")
        return jsonify({"success": status_code == 0, "message": message})
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(
            f"SQLAlchemy error adding to cart for user {current_user.id}: {str(e)}"
        )
        return jsonify({"message": "Database error", "error": str(e)}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(
            f"Unexpected error adding to cart for user {current_user.id}: {str(e)}"
        )
        return jsonify({"message": "Unexpected error", "error": str(e)}), 500





@cart_bp.route("/cart", methods=["GET"])
@token_required
def view_cart(current_user):
    try:
        # First, check if the user has an active cart
        cart_query = """
        SELECT id FROM cart 
        WHERE user_id = :user_id AND is_checked_out = 0
        """
        cart_result = db.session.execute(cart_query, {"user_id": current_user.id})
        cart = cart_result.fetchone()
        
        # If no active cart, return empty response
        if not cart:
            logger.info(f"No active cart found for user {current_user.id}")
            return jsonify({
                "success": True,
                "message": "Cart is empty.",
                "data": [],
                "total_price": 0
            }), 200
            
        cart_id = cart[0]
        logger.debug(f"Found active cart with ID: {cart_id} for user {current_user.id}")
        
        # Get cart items with explicit column names
        items_query = """
        SELECT 
            cd.id as cart_item_id,
            p.id as product_id,
            p.product_name,
            cd.quantity,
            p.price as unit_price,
            p.discount,
            (p.price * (1 - p.discount/100.0) * cd.quantity) as item_total
        FROM 
            cart_details cd
        JOIN 
            products p ON cd.product_id = p.id
        WHERE 
            cd.cart_id = :cart_id
        """
        
        items_result = db.session.execute(items_query, {"cart_id": cart_id})
        items = items_result.fetchall()
        
        if not items:
            logger.info(f"Cart {cart_id} is empty for user {current_user.id}")
            return jsonify({
                "success": True,
                "message": "Cart is empty.",
                "data": [],
                "total_price": 0
            }), 200
            
        # Format cart items with explicit debugging
        formatted_items = []
        total_price = 0
        
        for item in items:
            # Debug the raw item data
            logger.debug(f"Raw cart item data: {item}")
            
            # Create a dictionary with explicit keys
            item_dict = {
                "cart_item_id": item[0],  # This should be the cart_details.id
                "product_id": item[1],
                "product_name": item[2],
                "quantity": item[3],
                "unit_price": float(item[4]) if isinstance(item[4], Decimal) else item[4],
                "discount": float(item[5]) if isinstance(item[5], Decimal) else item[5],
                "item_total": float(item[6]) if isinstance(item[6], Decimal) else item[6]
            }
            
            # Debug the formatted item
            logger.debug(f"Formatted cart item: {item_dict}")
            
            formatted_items.append(item_dict)
            total_price += item_dict["item_total"]
            
        logger.info(f"Retrieved {len(formatted_items)} items for cart {cart_id}")
        return jsonify({
            "success": True,
            "message": "Cart retrieved successfully",
            "data": formatted_items,
            "total_price": round(total_price, 2)
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving cart: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while retrieving cart",
            "error": str(e),
            "error_type": type(e).__name__
        }), 500



@cart_bp.route("/cart/update", methods=["POST"])
@token_required
def update_cart_item_quantity(current_user):
    if not request.is_json:
        logger.error("Invalid JSON format in request")
        return jsonify({"success": False, "message": "Invalid JSON format"}), 400

    try:
        data = request.get_json()
        logger.debug(f"Received data: {data}")
        
        cart_item_id = data.get("cart_item_id")
        change = data.get("change")
        
        logger.debug(f"Extracted cart_item_id: {cart_item_id}, change: {change}")

        if not cart_item_id or change is None:
            logger.error("Missing cart_item_id or change in request")
            return jsonify({"success": False, "message": "Cart item ID and change value are required"}), 400

        # Check if the cart item exists
        cart_item_check = db.session.execute(
            "SELECT id FROM cart_details WHERE id = :cart_item_id",
            {"cart_item_id": cart_item_id}
        ).fetchone()
        
        if not cart_item_check:
            logger.error(f"Cart item with ID {cart_item_id} not found")
            return jsonify({"success": False, "message": f"Cart item with ID {cart_item_id} not found"}), 404

        # Check if the cart item belongs to the current user
        cart_check_query = """
        SELECT c.user_id 
        FROM cart_details cd
        JOIN cart c ON cd.cart_id = c.id
        WHERE cd.id = :cart_item_id
        """
        
        cart_check = db.session.execute(
            cart_check_query,
            {"cart_item_id": cart_item_id},
        ).fetchone()
        
        logger.debug(f"Cart check result: {cart_check}")

        if not cart_check:
            logger.error(f"Cart item with ID {cart_item_id} not found in any cart")
            return jsonify({"success": False, "message": "Cart item not found"}), 404
            
        if cart_check[0] != current_user.id:
            logger.warning(
                f"Unauthorized attempt to update cart item {cart_item_id} by user {current_user.id}"
            )
            return jsonify({"success": False, "message": "Unauthorized access to cart item"}), 403

        # Get current quantity
        current_quantity = db.session.execute(
            "SELECT quantity FROM cart_details WHERE id = :cart_item_id",
            {"cart_item_id": cart_item_id}
        ).scalar()
        
        new_quantity = current_quantity + change
        
        if new_quantity <= 0:
            logger.warning(f"Invalid new quantity {new_quantity} for cart item {cart_item_id}")
            return jsonify({"success": False, "message": "Quantity must be greater than 0"}), 400
            
        # Update the quantity
        db.session.execute(
            "UPDATE cart_details SET quantity = :new_quantity WHERE id = :cart_item_id",
            {"cart_item_id": cart_item_id, "new_quantity": new_quantity}
        )
        
        db.session.commit()
        logger.info(f"Updated quantity for cart item {cart_item_id} to {new_quantity}")
        
        return jsonify({
            "success": True, 
            "message": "Quantity updated successfully",
            "new_quantity": new_quantity
        }), 200
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating cart item quantity: {str(e)}")
        return jsonify({
            "success": False, 
            "message": "An error occurred while updating quantity",
            "error": str(e)
        }), 500



@cart_bp.route("/cart/remove", methods=["POST"])
@token_required
def remove_from_cart(current_user):
    if not request.is_json:
        logger.error("Invalid JSON format in request")
        return jsonify({"success": False, "message": "Invalid JSON format"}), 400

    try:
        data = request.get_json()
        logger.debug(f"Received data: {data}")
        
        cart_item_id = data.get("cart_item_id")
        logger.debug(f"Extracted cart_item_id: {cart_item_id}")

        if not cart_item_id:
            logger.error("Missing cart_item_id in request")
            return jsonify({"success": False, "message": "Cart item ID is required"}), 400

        # Check if the cart item exists
        cart_item_check = db.session.execute(
            "SELECT id FROM cart_details WHERE id = :cart_item_id",
            {"cart_item_id": cart_item_id}
        ).fetchone()
        
        if not cart_item_check:
            logger.error(f"Cart item with ID {cart_item_id} not found")
            return jsonify({"success": False, "message": f"Cart item with ID {cart_item_id} not found"}), 404

        # Check if the cart item belongs to the current user
        cart_check_query = """
        SELECT c.user_id 
        FROM cart_details cd
        JOIN cart c ON cd.cart_id = c.id
        WHERE cd.id = :cart_item_id
        """
        
        cart_check = db.session.execute(
            cart_check_query,
            {"cart_item_id": cart_item_id},
        ).fetchone()
        
        logger.debug(f"Cart check result: {cart_check}")

        if not cart_check:
            logger.error(f"Cart item with ID {cart_item_id} not found in any cart")
            return jsonify({"success": False, "message": "Cart item not found"}), 404
            
        if cart_check[0] != current_user.id:
            logger.warning(
                f"Unauthorized attempt to remove cart item {cart_item_id} by user {current_user.id}"
            )
            return jsonify({"success": False, "message": "Unauthorized access to cart item"}), 403

        # Instead of using a stored procedure, let's use a direct SQL query for debugging
        try:
            delete_query = """
            DELETE FROM cart_details
            WHERE id = :cart_item_id
            """
            
            result = db.session.execute(
                delete_query,
                {"cart_item_id": cart_item_id}
            )
            
            affected_rows = result.rowcount
            db.session.commit()
            
            if affected_rows > 0:
                logger.info(f"Removed cart item {cart_item_id} for user {current_user.id}")
                return jsonify({"success": True, "message": "Item removed from cart successfully"}), 200
            else:
                logger.warning(f"No rows affected when removing cart item {cart_item_id}")
                return jsonify({"success": False, "message": "Failed to remove item from cart"}), 400
                
        except Exception as sql_error:
            db.session.rollback()
            logger.error(f"SQL error when removing cart item: {str(sql_error)}")
            return jsonify({"success": False, "message": f"Database error: {str(sql_error)}"}), 500
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error removing from cart: {str(e)}")
        return jsonify({"success": False, "message": f"Unexpected error: {str(e)}"}), 500
