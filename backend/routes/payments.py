from flask import Blueprint, request, jsonify
from backend.extensions import db
from backend.models import Payment, Order
from datetime import datetime

payment_bp = Blueprint('payment', __name__)

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


