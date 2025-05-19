from flask import Blueprint, request, jsonify, current_app
from backend.extensions import db
from backend.models import Payment, Order
from datetime import datetime
import stripe
from backend.routes.auth import token_required
import logging

logger = logging.getLogger(__name__)

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/create-checkout-session', methods=['POST'])
@token_required
def create_checkout_session(current_user):
    try:
        logger.info(f"Creating checkout session for user {current_user.id}")
        
        # Check if Stripe API key is configured
        if not stripe.api_key:
            logger.error("Stripe API key is not configured")
            return jsonify({
                "success": False,
                "message": "Payment service is not configured properly"
            }), 500
        
        data = request.get_json()
        logger.info(f"Request data: {data}")
        
        order_id = data.get('order_id')
        if not order_id:
            logger.error("Missing order_id in request")
            return jsonify({"success": False, "message": "Order ID is required"}), 400
            
        logger.info(f"Getting details for order {order_id}")
        
        # Get order details
        order_query = """
        SELECT o.id, o.total_amount, o.shipping_address
        FROM orders o
        WHERE o.id = :order_id AND o.user_id = :user_id AND o.status = 'Pending'
        """
        
        order_result = db.session.execute(
            order_query, 
            {"order_id": order_id, "user_id": current_user.id}
        ).fetchone()
        
        if not order_result:
            logger.error(f"Order {order_id} not found or not pending for user {current_user.id}")
            return jsonify({"success": False, "message": "Order not found or not in pending status"}), 404
            
        logger.info(f"Order found: {order_result}")
        order_id, total_amount, shipping_address = order_result
        
        # Get order items
        items_query = """
        SELECT p.product_name, od.quantity, od.price, od.discount
        FROM order_details od
        JOIN products p ON od.product_id = p.id
        WHERE od.order_id = :order_id
        """
        
        items_result = db.session.execute(items_query, {"order_id": order_id}).fetchall()
        logger.info(f"Found {len(items_result)} items for order {order_id}")
        
        # Create line items for Stripe
        line_items = []
        for item in items_result:
            product_name, quantity, price, discount = item
            discounted_price = price * (1 - discount/100)
            
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product_name,
                    },
                    'unit_amount': int(discounted_price * 100),  # Convert to cents
                },
                'quantity': quantity,
            })
        
        # Add a fallback item if no items were found
        if not line_items:
            logger.warning(f"No items found for order {order_id}, using total amount")
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f"Order #{order_id}",
                    },
                    'unit_amount': int(total_amount * 100),  # Convert to cents
                },
                'quantity': 1,
            })
        
        logger.info(f"Creating Stripe checkout session with {len(line_items)} items")
        
        # Get frontend URL from config
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:3000')
        logger.info(f"Frontend URL: {frontend_url}")
        
        # Create Stripe Checkout session
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=f"{frontend_url}/order/success?session_id={{CHECKOUT_SESSION_ID}}&order_id={order_id}",
                cancel_url=f"{frontend_url}/order/cancel?order_id={order_id}",
                metadata={
                    'order_id': str(order_id),
                    'user_id': str(current_user.id)
                }
            )
            
            logger.info(f"Checkout session created: {checkout_session.id}")
            
            # Return the session ID to the client
            return jsonify({
                "success": True,
                "message": "Checkout session created",
                "sessionId": checkout_session.id,
                "url": checkout_session.url
            }), 200
            
        except stripe.error.StripeError as se:
            logger.error(f"Stripe error creating checkout session: {str(se)}")
            return jsonify({
                "success": False,
                "message": f"Payment processing error: {str(se)}"
            }), 400
            
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Payment processing error: {str(e)}"
        }), 400
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        return jsonify({
            "success": False,
            "message": "An error occurred while creating checkout session",
            "error": str(e)
        }), 500

@payment_bp.route('/payment/create/<int:order_id>', methods=['POST'])
def create_payment(order_id):
    order = Order.query.get_or_404(order_id)
    if order.status != 'Pending':
        return jsonify({'message': 'Order is not pending'}), 400

    data = request.get_json()
    payment_method = data.get('payment_method', 'Cash on Delivery')  # Default: Cash on delivery
    # Create payment
    new_payment = Payment(
        order_id=order_id,
        amount=order.total_amount,
        payment_method=payment_method,
        payment_status='Pending',
        payment_date=datetime.utcnow()
    )
    db.session.add(new_payment)

    # Update order status
    order.status = 'Processing'
    db.session.commit()

    return jsonify({'message': 'Payment created successfully', 'payment_id': new_payment.id}), 201

@payment_bp.route('/payment/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    return jsonify({
        'id': payment.id,
        'order_id': payment.order_id,
        'amount': float(payment.amount),
        'payment_method': payment.payment_method,
        'payment_status': payment.payment_status,
        'payment_date': payment.payment_date.isoformat()
    }) 


