from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from backend.routes.auth import token_required
from backend.extensions import db
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

checkout_bp = Blueprint('checkout', __name__)

def check_admin(current_user):
    return current_user.user_role.lower() == 'admin'
    
#################################################### create_order ####################################################  
@checkout_bp.route('/checkout', methods=['POST'])
@token_required
def create_order(current_user):
    if not request.is_json:
        logger.error("Invalid JSON format in request")
        return jsonify({'message': 'Invalid JSON format'}), 400

    data = request.get_json()
    shipping_address = data.get('shipping_address')
    payment_method = data.get('payment_method')

    if not shipping_address or not payment_method:
        logger.error("Missing shipping_address or payment_method in request")
        return jsonify({'message': 'Shipping address and payment method are required'}), 400

    try:
        # Get active cart for the user
        cart = db.session.execute(
            "SELECT id FROM Cart WHERE user_id = :user_id AND is_checked_out = 0",
            {"user_id": current_user.id}
        ).fetchone()

        if not cart:
            logger.warning(f"No active cart found for user {current_user.id}")
            return jsonify({
                'success': False,
                'message': 'No active cart found'
            }), 400

        cart_id = cart[0]
        
        # Calculate total amount from cart_details, considering discount
        total_amount = db.session.execute(
            "SELECT SUM(quantity * price * (1 - discount / 100)) FROM cart_details WHERE cart_id = :cart_id",
            {"cart_id": cart_id}
        ).scalar()

        total_amount = float(total_amount) if total_amount is not None else 0.00
        print(total_amount)

        # Execute stored procedure to create order
        result = db.session.execute(
            "EXEC CreateOrder @UserID=:user_id, @ShippingAddress=:shipping_address, @TotalAmount=:total_amount, @PaymentMethod=:payment_method",
            {
                "user_id": current_user.id,
                "shipping_address": shipping_address,
                "total_amount": total_amount,
                "payment_method": payment_method
            }
        )
        rows = result.fetchall()
        db.session.commit()
    
        # Check if we got a result
        if rows:
            row = rows[0]  # Take the first row (assuming single result)
            status, status_code, message, order_id = row
            print(status, status_code, message, order_id)
            if status == 'success':
                logger.info(f"Order {order_id} created successfully for user {current_user.id}")
                return jsonify({
                    'success': True,
                    'message': message,
                    'order_id': order_id
                }), 200
            else:
                logger.warning(f"Failed to create order for user {current_user.id}: {message}")
                return jsonify({
                    'success': False,
                    'message': message
                }), 400 if status_code in (1, 3, 4) else 500
        else:
            logger.error(f"No result returned from CreateOrder for user {current_user.id}")
            return jsonify({
                'success': False,
                'message': 'No result returned from order creation'
            }), 500

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"SQLAlchemy error during checkout for user {current_user.id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Database error',
            'error': str(e)
        }), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error during checkout for user {current_user.id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Unexpected error',
            'error': str(e)
        }), 500
    
################################################################ get_order_details ########################################
@checkout_bp.route('/order/<int:order_id>', methods=['GET'])
@token_required
def get_order_details(current_user, order_id):
    try:
        # Execute the Stored Procedure to get order details
        result = db.session.execute(
            "EXEC GetOrderDetails @order_id=:order_id",
            {"order_id": order_id}
        )
        order_row = result.fetchone()

        # Check if the stored procedure returned a failure status
        if order_row and order_row[0] == 'fail':
            result.close()
            logger.warning(f"Order {order_id} not found for user {current_user.id}")
            return jsonify({
                "status": "error",
                "message": order_row[1]
            }), 404

        # Check if order exists and belongs to the current user
        if not order_row or order_row[1] != current_user.id:
            result.close()
            logger.warning(f"Order {order_id} not found or unauthorized access by user {current_user.id}")
            return jsonify({
                "status": "error",
                "message": "Order not found or you do not have access to this order"
            }), 404

        # Order exists, format the data
        order = {
            "id": order_row[0],
            "user_id": order_row[1],
            "username": order_row[2],
            "full_name": order_row[3],
            "user_address": order_row[4],
            "phone_number": order_row[5],
            "total_amount": float(order_row[6]) if order_row[6] is not None else 0.0,
            "status": order_row[7],
            "order_date": str(order_row[8]) if order_row[8] else None
        }
        result.close()

        # Fetch order items
        result = db.session.execute(
            "EXEC GetOrderItems @order_id=:order_id",
            {"order_id": order_id}
        )
        order_items = []
        for row in result.fetchall():
            order_items.append({
                "product_name": row[0],
                "quantity": int(row[1]),
                "unit_price": float(row[2]) if row[2] is not None else 0.0,
                "total_price_for_each_item_after_discount": float(row[3]) if row[3] is not None else 0.0
            })
        result.close()

        logger.info(f"Order {order_id} details retrieved successfully for user {current_user.id}")
        return jsonify({
            "status": "success",
            "message": "Order details retrieved successfully",
            "order": order,
            "order_items": order_items
        }), 200

    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error retrieving order {order_id} for user {current_user.id}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Database error: {str(e)}"
        }), 500
    except Exception as e:
        logger.error(f"Unexpected error retrieving order {order_id} for user {current_user.id}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }), 500

################################################################ checkout info ########################################
@checkout_bp.route('/checkout', methods=['GET'])
@token_required
def checkout(current_user):
    try:
        # Get active cart for the user
        cart = db.session.execute(
            "SELECT id FROM Cart WHERE user_id = :user_id AND is_checked_out = 0",
            {"user_id": current_user.id}
        ).fetchone()

        if not cart:
            logger.warning(f"No active cart found for user {current_user.id}")
            return jsonify({
                "status": "error",
                "message": "No active cart found"
            }), 404

        cart_id = cart[0]

        # Fetch cart items
        result = db.session.execute(
            "SELECT p.product_name, cd.quantity, cd.price, cd.discount "
            "FROM cart_details cd "
            "JOIN products p ON cd.product_id = p.id "
            "WHERE cd.cart_id = :cart_id",
            {"cart_id": cart_id}
        )
        cart_items = []
        for row in result.fetchall():
            cart_items.append({
                "product_name": row[0],
                "quantity": int(row[1]),
                "unit_price": float(row[2]) if row[2] is not None else 0.0,
                "discount": float(row[3]) if row[3] is not None else 0.0,
                "total_price": float(row[1] * row[2] * (1 - row[3] / 100)) if row[2] and row[3] is not None else 0.0
            })
        result.close()

        # Calculate total amount
        total_amount = db.session.execute(
            "SELECT SUM(quantity * price * (1 - discount / 100)) FROM cart_details WHERE cart_id = :cart_id",
            {"cart_id": cart_id}
        ).scalar()

        total_amount = float(total_amount) if total_amount is not None else 0.00

        logger.info(f"Checkout details retrieved successfully for user {current_user.id}")
        return jsonify({
            "status": "success",
            "message": "Checkout details retrieved successfully",
            "cart_items": cart_items,
            "total_amount": round(total_amount, 2)
        }), 200

    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error during checkout for user {current_user.id}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Database error: {str(e)}"
        }), 500
    except Exception as e:
        logger.error(f"Unexpected error during checkout for user {current_user.id}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }), 500
    

# mahmoud 