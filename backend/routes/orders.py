from flask import Blueprint, jsonify, request
from backend.extensions import db
import logging
from decimal import Decimal
from sqlalchemy.exc import SQLAlchemyError
from backend.routes.auth import token_required

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

order_bp = Blueprint('order', __name__)

# Function to verify the user's role
def check_admin(current_user):
    return current_user.user_role.lower() == 'admin'
#######################################################################get_order_details########################################################
@order_bp.route('/order/<int:order_id>', methods=['GET', 'DELETE'])
@token_required
def manage_order(current_user, order_id):
    if request.method == 'GET':
        try:
            logger.debug(f"Fetching details for order ID: {order_id}")
            result = db.session.execute(
                """
                EXEC GetOrderDetails @order_id=:order_id, @caller_user_id=:caller_user_id, @is_admin=:is_admin
                """,
                {
                    "order_id": order_id,
                    "caller_user_id": current_user.id,
                    "is_admin": 1 if check_admin(current_user) else 0
                }
            )
            order_row = result.fetchone()

            if order_row and 'status' in order_row.keys() and order_row['status'] == 'fail':
                result.close()
                logger.warning(f"Order fetch failed: {order_row['message']}")
                return jsonify({'message': order_row['message']}), 403 if order_row['message'] == 'You are not authorized to view this order.' else 404

            if not order_row:
                result.close()
                logger.warning(f"No order found for order_id: {order_id}")
                return jsonify({'message': 'Order not found'}), 404

            order = {
                "id": order_row[0],
                "user_id": order_row[1],
                "username": order_row[2],
                "full_name": order_row[3],
                "user_address": order_row[4],
                "phone_number": order_row[5],
                "total_amount": float(order_row[6]) if isinstance(order_row[6], Decimal) else order_row[6],
                "status": order_row[7],
                "order_date": str(order_row[8]),
                "can_cancel": order_row[7] not in ['shipped', 'delivered']  # إضافة حقل للدلالة على الإلغاء
            }
            result.close()

            logger.debug(f"Fetching items for order ID: {order_id}")
            result = db.session.execute(
                "EXEC GetOrderItems @order_id=:order_id",
                {"order_id": order_id}
            )
            order_items = []
            for row in result.fetchall():
                order_items.append({
                    "product_name": row[0],
                    "quantity": row[1],
                    "unit_price": float(row[2]) if isinstance(row[2], Decimal) else row[2],
                    "total_price": float(row[3]) if isinstance(row[3], Decimal) else row[3]
                })
            result.close()
            logger.info(f"Found {len(order_items)} items in order {order_id}")

            return jsonify({
                'order': order,
                'order_items': order_items
            }), 200

        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error fetching order details: {str(e)}")
            return jsonify({'message': 'Error fetching order details', 'error': str(e)}), 500
        except Exception as e:
            logger.error(f"General error fetching order details: {str(e)}")
            return jsonify({'message': 'Error fetching order details', 'error': str(e)}), 500

    elif request.method == 'DELETE':
        try:
            logger.debug(f"Attempting to cancel order ID: {order_id}")
            result = db.session.execute(
                """
                EXEC GetOrderDetails @order_id=:order_id, @caller_user_id=:caller_user_id, @is_admin=:is_admin
                """,
                {
                    "order_id": order_id,
                    "caller_user_id": current_user.id,
                    "is_admin": 1 if check_admin(current_user) else 0
                }
            )
            order_row = result.fetchone()
            result.close()

            if not order_row or order_row['user_id'] != current_user.id:
                return jsonify({'message': 'Order not found or unauthorized'}), 403

            if order_row['status'] in ['shipped', 'delivered']:
                return jsonify({'message': 'Cannot cancel order in this status'}), 403

            result = db.session.execute(
                "EXEC CancelOrder @order_id=:order_id",
                {"order_id": order_id}
            )
            row = result.fetchone()
            if row and row['status'] == 'success':
                db.session.commit()
                logger.info(f"Order {order_id} canceled by user {current_user.id}")
                return jsonify({'message': row['message']}), 200
            else:
                db.session.rollback()
                return jsonify({'message': row['message'] if row else 'Error canceling order'}), 400
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"SQLAlchemy error: {str(e)}")
            return jsonify({'message': 'Error canceling order', 'error': str(e)}), 500
        except Exception as e:
            db.session.rollback()
            logger.error(f"General error: {str(e)}")
            return jsonify({'message': 'Error canceling order', 'error': str(e)}), 500
#######################################################################list_orders_of_user########################################################

@order_bp.route('/orders', methods=['GET'])
@token_required
def list_orders_of_user(current_user):
    try:
        result = db.session.execute(
            "EXEC GetAllOrders @user_id=:user_id",
            {"user_id": current_user.id}
        )
        orders = result.fetchall()
        formatted_orders = [{
            "id": row[0],
            "total_amount": float(row[1]) if isinstance(row[1], Decimal) else row[1],
            "status": row[2],
            "order_date": str(row[3])
        } for row in orders]
        logger.info(f"Found {len(formatted_orders)} orders for user {current_user.id}")
        return jsonify({'orders': formatted_orders}), 200
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error: {str(e)}")
        return jsonify({'message': 'Error fetching orders', 'error': str(e)}), 500
    except Exception as e:
        logger.error(f"General error: {str(e)}")
        return jsonify({'message': 'Error fetching orders', 'error': str(e)}), 500
    
# mahmoud