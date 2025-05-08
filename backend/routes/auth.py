from flask import Blueprint, request, jsonify
from backend.extensions import db
from backend.models import User
from backend.models import Order
import jwt
import logging
import datetime
from flask import current_app as app
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash


auth_bp = Blueprint('auth', __name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# ===== SIGNUP =====
@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json(force=True)
        username = data.get('username')
        password = data.get('pass_word')
        email = data.get('email')
        full_name = data.get('full_name')
        user_address = data.get('user_address')
        phone_number = data.get('phone_number')
        user_role = data.get('user_role', '').strip().lower()
        logger.debug(f"Received signup data: {data}")

        if not username or not password or not email:
            logger.warning("Missing required fields")
            return jsonify({'message': 'Missing required fields'}), 400

        if User.query.filter_by(username=username).first():
            logger.warning(f"Username {username} already exists")
            return jsonify({'message': 'Username already exists'}), 400

        if user_role not in ['customer', 'admin']:
            logger.warning(f"Invalid role value: {user_role}")
            return jsonify({'message': 'Invalid role value'}), 400
        
        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            pass_word=hashed_password,
            email=email,
            full_name=full_name,
            user_address=user_address,
            phone_number=phone_number,
            user_role=user_role
        )

        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully'}), 201

    except Exception as e:
        print("Error occurred:", str(e))
        return jsonify({'message': 'Internal Server Error'}), 500

# ===== LOGIN =====
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        if not request.is_json:
            logger.error("Invalid JSON format in request")
            return jsonify({'message': 'Invalid JSON format'}), 400
        
        data = request.get_json(force=True)
        logger.debug(f"Received data: {data}")

        username = data.get('username')
        password = data.get('pass_word')

        if not username or not password:
            logger.warning(f"Missing username or password: username={username}, password={password}")
            return jsonify({'message': 'Missing username or password'}), 400

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.pass_word, password):
            token = jwt.encode(
                {'user_id': user.id, 
                 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
                app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            logger.info(f"Generated token for user {username}: {token}")

            return jsonify({
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.user_role
                }
            }), 200
        else:
            logger.warning(f"Invalid credentials for username: {username}")
            return jsonify({'message': 'Invalid credentials'}), 401

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'message': 'Internal Server Error'}), 500

# ===== Token Required Decorator =====
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split()[1]
            except IndexError:
                logger.warning("Invalid Authorization header format")
                return jsonify({'message': 'Invalid Authorization header format'}), 401

        if not token:
            logger.warning("Token is missing")
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            logger.debug(f"Decoded token data: {data}")
            current_user = User.query.get(data['user_id'])
            if current_user is None:
                logger.warning(f"User not found for ID: {data['user_id']}")
                return jsonify({'message': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)
    
    return decorated

# ===== LOGOUT =====
@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    try:
        # For JWT, logout is client-side (discard token)
        logger.info(f"User {current_user.id} logged out")
        return jsonify({'message': 'Logout successful. Please discard your token.'}), 200
    except Exception as e:
        logger.error(f"Logout error for user {current_user.id}: {str(e)}")
        return jsonify({'message': 'Internal Server Error', 'error': str(e)}), 500
    
# ===== USER PROFILE =====
@auth_bp.route('/profile', methods=['GET'])
@token_required
def profile(current_user):
    try:
        user_data = {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'phone': current_user.phone_number,
            'address': current_user.user_address,
            'number_of_orders': Order.query.filter_by(user_id=current_user.id).count()
        }

        orders = Order.query.filter_by(user_id=current_user.id).all()
        orders_list = []
        for order in orders:
            orders_list.append({
                'order_id': order.id,
                'total_price': order.total_amount,
                'status': order.status,
                'created_at': order.order_date
            })

        logger.info(f"Profile retrieved for user {current_user.username}")
        return jsonify({
            'user_profile': user_data,
            'orders': orders_list
        }), 200

    except Exception as e:
        logger.error(f"Profile error: {str(e)}")
        return jsonify({'message': 'Internal Server Error', 'error': str(e)}), 500
    
# mahmoud