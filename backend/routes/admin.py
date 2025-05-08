from flask import Blueprint, request, jsonify
from backend.extensions import db
from backend.models import User
import json
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange, Regexp, ValidationError
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from decimal import Decimal
from backend.routes.auth import token_required

admin_bp = Blueprint('admin', __name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Function to verify the user's role
def check_admin(current_user):
    return current_user.user_role.lower() == 'admin'

# Helper function to parse JSON result
def parse_json_result(result):
    if result and result[0][0]:
        try:
            return json.loads(result[0][0])
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON data: {str(e)}")
            return []
    return []

# ===== WTForms for Validation =====
class AddProductForm(FlaskForm):
    class Meta:
        csrf = False  # Disable CSRF for API

    product_name = StringField('Product Name', validators=[
        DataRequired(), 
        Length(min=1, max=100)
    ])
    description = StringField('Description', validators=[
        Length(max=500)
    ])
    price = FloatField('Price', validators=[
        DataRequired(), 
        NumberRange(min=0.01, message="Price must be greater than 0")
    ])
    stock = IntegerField('Stock', validators=[
        DataRequired(), 
        NumberRange(min=0, message="Stock cannot be negative")
    ])
    category_id = IntegerField('Category ID', validators=[
        DataRequired()
    ])
    image_url = StringField('Image URL', validators=[
        Regexp(r'^(https?://)?([a-zA-Z0-9-]+\.)+[a-zA-Z0-9-]+(/[a-zA-Z0-9-./?%&=]*)?$', 
               message="Invalid URL format")
    ])
    discount = FloatField('Discount', validators=[
        NumberRange(min=0, max=100, message="Discount must be between 0 and 100")
    ])

    def validate_category_id(self, field):
        result = db.session.execute("SELECT id FROM categories WHERE id = :category_id", {"category_id": field.data})
        if not result.fetchone():
            raise ValidationError('Invalid category ID')

class UpdatePriceForm(FlaskForm):
    class Meta:
        csrf = False  # Disable CSRF for API

    new_price = FloatField('New Price', validators=[
        DataRequired(), 
        NumberRange(min=0.01, message="Price must be greater than 0")
    ])

class UpdateDiscountForm(FlaskForm):
    class Meta:
        csrf = False  # Disable CSRF for API

    new_discount = FloatField('New Discount', validators=[
        DataRequired(), 
        NumberRange(min=0, max=100, message="Discount must be between 0 and 100")
    ])

# ########################################################################################################################

@admin_bp.route('/admin', methods=['GET'])
@token_required
def admin_dashboard(current_user):
    # user_id = 1  Temporary, it will change when we add the login
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({'message': 'Unauthorized access'}), 403
    return jsonify({'message': 'Welcome to the admin dashboard'}), 200

# ###########################################################################################################################

@admin_bp.route('/admin/products', methods=['GET'])
@token_required
def manage_products(current_user):
    # user_id = 1   Temporary, it will change when we add the login
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({'message': 'Unauthorized access'}), 403

    try:
        result_products = db.session.execute("EXEC GetAllProducts")
        products = result_products.fetchall()
        formatted_products = []
        for row in products:
            formatted_products.append({
                "id": row[0],
                "product_name": row[1],
                "product_description": row[2],
                "price": float(row[3]) if isinstance(row[3], Decimal) else row[3],
                "stock": row[4],
                "category_id": row[5],
                "category_name": row[6],
                "image_url": row[7],
                "discount": float(row[8]) if isinstance(row[8], Decimal) else row[8]
            })

        categories = db.session.execute("SELECT id, category_name FROM categories").fetchall()
        formatted_categories = [{"id": row[0], "category_name": row[1]} for row in categories]

        logger.info(f"Retrieved {len(formatted_products)} products and {len(formatted_categories)} categories")
        return jsonify({
            'products': formatted_products,
            'categories': formatted_categories
        }), 200

    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error fetching products: {str(e)}")
        return jsonify({'message': 'Error fetching products', 'error': str(e)}), 500
    except Exception as e:
        logger.error(f"General error fetching products: {str(e)}")
        return jsonify({'message': 'Error fetching products', 'error': str(e)}), 500

# ############################################################################################################################

@admin_bp.route('/admin/product/add', methods=['POST'])
@token_required
def add_product(current_user):
    # user_id = 1   Temporary, it will change when we add the login
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({'message': 'Unauthorized access'}), 403

    if not request.is_json:
        logger.error("Invalid JSON format in request")
        return jsonify({'message': 'Invalid JSON format'}), 400

    form = AddProductForm(data=request.get_json(force=True))
    
    if not form.validate():
        errors = {field.name: field.errors for field in form}
        logger.debug(f"Validation errors: {errors}")
        return jsonify({'message': 'Validation error', 'errors': errors}), 400

    try:
        query = text("""
            EXEC AddNewProduct 
                @product_name=:product_name, 
                @description=:description, 
                @price=:price, 
                @stock=:stock, 
                @category_id=:category_id, 
                @image_url=:image_url, 
                @discount=:discount
        """)
        result = db.session.execute(
            query,
            {
                "product_name": form.product_name.data,
                "description": form.description.data or '',
                "price": form.price.data,
                "stock": form.stock.data,
                "category_id": form.category_id.data,
                "image_url": form.image_url.data or '',
                "discount": form.discount.data or 0.0
            }
        )

        logger.debug("Fetching result...")
        row = result.fetchone()
        if row:
            status = row['status']
            message = row['message']
            logger.debug(f"Status: {status}, Message: {message}")
            if status == 'success':
                db.session.commit()
                logger.info(f"Product {form.product_name.data} added successfully")
                return jsonify({'message': message}), 201
            else:
                db.session.rollback()
                return jsonify({'message': message}), 400
        else:
            db.session.rollback()
            logger.error("Error adding product: No response from database")
            return jsonify({'message': 'Error adding product: No response from database'}), 500

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"SQLAlchemy error adding product: {str(e)}")
        return jsonify({'message': 'Error adding product', 'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"General error adding product: {str(e)}")
        return jsonify({'message': 'Error adding product', 'error': str(e)}), 500

# ###################################################################################################################################

@admin_bp.route('/admin/product/delete/<int:product_id>', methods=['DELETE'])
@token_required
def delete_product(current_user, product_id):
    # user_id = 1   Temporary, it will change when we add the login
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({'message': 'Unauthorized access'}), 403

    # Fetch product name based on ID
    product_name_result = db.session.execute(
        "SELECT product_name FROM products WHERE id = :product_id",
        {"product_id": product_id}
    ).fetchone()

    if not product_name_result:
        logger.warning(f"Product not found for ID: {product_id}")
        return jsonify({'message': 'Product not found'}), 404

    product_name = product_name_result[0]

    try:
        query = text("""
            EXEC DeleteProduct 
                @product_name=:product_name, 
                @ConfirmDeletion=:confirm_deletion
        """)
        result = db.session.execute(
            query,
            {
                "product_name": product_name,
                "confirm_deletion": "Yes"
            }
        )

        logger.debug("Fetching result...")
        row = result.fetchone()
        if row:
            status = row['status']
            message = row['message']
            logger.debug(f"Status: {status}, Message: {message}")
            if status == 'success':
                db.session.commit()
                logger.info(f"Product {product_name} deleted successfully")
                return jsonify({'message': message}), 200
            else:
                db.session.rollback()
                return jsonify({'message': message}), 400
        else:
            db.session.rollback()
            logger.error("Error deleting product: No response from database")
            return jsonify({'message': 'Error deleting product: No response from database'}), 500

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"SQLAlchemy error deleting product: {str(e)}")
        return jsonify({'message': 'Error deleting product', 'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"General error deleting product: {str(e)}")
        return jsonify({'message': 'Error deleting product', 'error': str(e)}), 500

# ########################################################################################### update_product_price ########################################################

@admin_bp.route('/admin/product/update-price/<int:product_id>', methods=['POST'])
@token_required
def update_product_price(current_user, product_id):
    # user_id = 1   Temporary, it will change when we add the login
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({'message': 'Unauthorized access'}), 403

    if not request.is_json:
        logger.error("Invalid JSON format in request")
        return jsonify({'message': 'Invalid JSON format'}), 400

    form = UpdatePriceForm(data=request.get_json(force=True))

    if not form.validate():
        errors = {field.name: field.errors for field in form}
        logger.debug(f"Validation errors: {errors}")
        return jsonify({'message': 'Validation error', 'errors': errors}), 400

    # Fetch the product name
    product_name_result = db.session.execute(
        "SELECT product_name FROM products WHERE id = :product_id",
        {"product_id": product_id}
    ).fetchone()

    if not product_name_result:
        logger.warning(f"Product not found for ID: {product_id}")
        return jsonify({'message': 'Product not found'}), 404

    product_name = product_name_result[0]

    try:
        query = text("""
            EXEC UpdateProductPrice 
                @product_name=:product_name, 
                @new_price=:new_price
        """)
        result = db.session.execute(
            query,
            {
                "product_name": product_name,
                "new_price": form.new_price.data
            }
        )

        logger.debug("Fetching result...")
        row = result.fetchone()
        if row:
            status = row['status']
            message = row['message']
            logger.debug(f"Status: {status}, Message: {message}")
            if status == 'success':
                db.session.commit()
                logger.info(f"Price updated for product {product_name}")
                return jsonify({'message': message}), 200
            else:
                db.session.rollback()
                return jsonify({'message': message}), 400
        else:
            db.session.rollback()
            logger.error("Error updating price: No response from database")
            return jsonify({'message': 'Error updating price: No response from database'}), 500

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"SQLAlchemy error updating price: {str(e)}")
        return jsonify({'message': 'Error updating price', 'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"General error updating price: {str(e)}")
        return jsonify({'message': 'Error updating price', 'error': str(e)}), 500

# ########################################################################################### update_product_discount ###############################################################

@admin_bp.route('/admin/product/update-discount/<int:product_id>', methods=['POST'])
@token_required
def update_product_discount(current_user, product_id):
    # user_id = 1  Temporary, it will change when we add the login
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({'message': 'Unauthorized access'}), 403

    if not request.is_json:
        logger.error("Invalid JSON format in request")
        return jsonify({'message': 'Invalid JSON format'}), 400

    form = UpdateDiscountForm(data=request.get_json(force=True))

    if not form.validate():
        errors = {field.name: field.errors for field in form}
        logger.debug(f"Validation errors: {errors}")
        return jsonify({'message': 'Validation error', 'errors': errors}), 400

    # Fetch the product name
    product_name_result = db.session.execute(
        "SELECT product_name FROM products WHERE id = :product_id",
        {"product_id": product_id}
    ).fetchone()

    if not product_name_result:
        logger.warning(f"Product not found for ID: {product_id}")
        return jsonify({'message': 'Product not found'}), 404

    product_name = product_name_result[0]

    try:
        query = text("""
            EXEC AddProductDiscount 
                @product_name=:product_name, 
                @new_discount=:new_discount
        """)
        result = db.session.execute(
            query,
            {
                "product_name": product_name,
                "new_discount": form.new_discount.data
            }
        )

        logger.debug("Fetching result...")
        row = result.fetchone()
        if row:
            status = row['status']
            message = row['message']
            logger.debug(f"Status: {status}, Message: {message}")
            if status == 'success':
                db.session.commit()
                logger.info(f"Discount updated for product {product_name}")
                return jsonify({'message': message}), 200
            else:
                db.session.rollback()
                return jsonify({'message': message}), 400
        else:
            db.session.rollback()
            logger.error("Error updating discount: No response from database")
            return jsonify({'message': 'Error updating discount: No response from database'}), 500

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"SQLAlchemy error updating discount: {str(e)}")
        return jsonify({'message': 'Error updating discount', 'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"General error updating discount: {str(e)}")
        return jsonify({'message': 'Error updating discount', 'error': str(e)}), 500

# ####################################################################################################################################################################

@admin_bp.route('/admin/orders', methods=['GET'])
@token_required
def manage_orders(current_user):
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({'message': 'Unauthorized access'}), 403

    try:
        logger.debug("Fetching orders...")
        result = db.session.execute("EXEC GetAllOrders")
        first_row = result.fetchone()

        formatted_orders = []
        if first_row and 'status' in first_row.keys() and first_row['status'] == 'fail':
            logger.info("No orders found")
            return jsonify({'message': first_row['message']}), 200
        else:
            if first_row:
                formatted_orders.append({
                    "id": first_row[0],
                    "user_id": first_row[1],
                    "username": first_row[2],
                    "full_name": first_row[3],
                    "user_address": first_row[4],
                    "phone_number": first_row[5],
                    "total_amount": float(first_row[6]) if isinstance(first_row[6], Decimal) else first_row[6],
                    "status": first_row[7],
                    "order_date": str(first_row[8])  # Convert to string for JSON
                })
            for row in result.fetchall():
                formatted_orders.append({
                    "id": row[0],
                    "user_id": row[1],
                    "username": row[2],
                    "full_name": row[3],
                    "user_address": row[4],
                    "phone_number": row[5],
                    "total_amount": float(row[6]) if isinstance(row[6], Decimal) else row[6],
                    "status": row[7],
                    "order_date": str(row[8])  # Convert to string for JSON
                })
            logger.info(f"Found {len(formatted_orders)} orders")

        return jsonify({'orders': formatted_orders}), 200

    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error fetching orders: {str(e)}")
        return jsonify({'message': 'Error fetching orders', 'error': str(e)}), 500
    except Exception as e:
        logger.error(f"General error fetching orders: {str(e)}")
        return jsonify({'message': 'Error fetching orders', 'error': str(e)}), 500

# #################################################################################### get_order_details ################################################################################

@admin_bp.route('/admin/order/<int:order_id>', methods=['GET'])
@token_required
def get_order_details(current_user, order_id):
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({'message': 'Unauthorized access'}), 403

    try:
        logger.debug(f"Fetching details for order ID: {order_id}")
        result = db.session.execute(
            """
            EXEC GetOrderDetails @order_id=:order_id, @caller_user_id=:caller_user_id, @is_admin=:is_admin
            """,
            {
                "order_id": order_id,
                "caller_user_id": current_user.id,
                "is_admin": check_admin(current_user)
            }
        )
        order_row = result.fetchone()

        if order_row and 'status' in order_row.keys() and order_row['status'] == 'fail':
            result.close()
            logger.warning(f"Order fetch failed: {order_row['message']}")
            return jsonify({'message': order_row['message']}), 403 if order_row['message'] == 'You are not authorized to view this order.' else 404

        order = {
            "id": order_row[0],
            "user_id": order_row[1],
            "username": order_row[2],
            "full_name": order_row[3],
            "user_address": order_row[4],
            "phone_number": order_row[5],
            "total_amount": float(order_row[6]) if isinstance(order_row[6], Decimal) else order_row[6],
            "status": order_row[7],
            "order_date": str(order_row[8])  # Convert to string for JSON
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

# ######################################################################################################################################

@admin_bp.route('/admin/users', methods=['GET'])
@token_required
def manage_users(current_user):
    # user_id = 1   Temporary, it will change when we add the login
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({'message': 'Unauthorized access'}), 403

    try:
        result = db.session.execute("EXEC GetAllUsers")
        users = result.fetchall()
        formatted_users = []
        for row in users:
            formatted_users.append({
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "full_name": row[3],
                "user_address": row[4],
                "user_role": row[6],
                "phone_number": row[5]
            })

        logger.info(f"Retrieved {len(formatted_users)} users")
        return jsonify({'users': formatted_users}), 200

    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error fetching users: {str(e)}")
        return jsonify({'message': 'Error fetching users', 'error': str(e)}), 500
    except Exception as e:
        logger.error(f"General error fetching users: {str(e)}")
        return jsonify({'message': 'Error fetching users', 'error': str(e)}), 500

# ##########################################################################################################################################
@admin_bp.route('/admin/reviews', methods=['GET'])
@token_required
def manage_reviews(current_user):
    # user_id = 1   Temporary, it will change when we add the login
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({'message': 'Unauthorized access'}), 403

    try:
        logger.debug("Fetching all reviews...")
        result = db.session.execute("EXEC GetAllReviews")
        first_row = result.fetchone()

        formatted_reviews = []
        if first_row and 'status' in first_row.keys() and first_row['status'] == 'fail':
            logger.info("No reviews found")
            return jsonify({'message': first_row['message']}), 200
        else:
            if first_row:
                formatted_reviews.append({
                    "product_id": first_row[0],
                    "product_name": first_row[1],
                    "user_id": first_row[2],
                    "username": first_row[3],
                    "full_name": first_row[4],
                    "rating": float(first_row[5]) if isinstance(first_row[5], Decimal) else first_row[5],
                    "review_text": first_row[6],
                    "review_date": str(first_row[7])  # Convert to string for JSON
                })
            for row in result.fetchall():
                formatted_reviews.append({
                    "product_id": row[0],
                    "product_name": row[1],
                    "user_id": row[2],
                    "username": row[3],
                    "full_name": row[4],
                    "rating": float(row[5]) if isinstance(row[5], Decimal) else row[5],
                    "review_text": row[6],
                    "review_date": str(row[7])  # Convert to string for JSON
                })
            logger.info(f"Retrieved {len(formatted_reviews)} reviews")

        return jsonify({'reviews': formatted_reviews}), 200

    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error fetching reviews: {str(e)}")
        return jsonify({'message': 'Error fetching reviews', 'error': str(e)}), 500
    except Exception as e:
        logger.error(f"General error fetching reviews: {str(e)}")
        return jsonify({'message': 'Error fetching reviews', 'error': str(e)}), 500
# ##########################################################################################################################################

@admin_bp.route('/admin/review/delete/<int:product_id>/<int:user_id>', methods=['DELETE'])
@token_required
def delete_review(current_user, product_id, user_id):
    
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({'message': 'Unauthorized access'}), 403

    try:
        product_name_result = db.session.execute(
            "SELECT product_name FROM products WHERE id = :product_id",
            {"product_id": product_id}
        ).fetchone()
        if not product_name_result:
            logger.warning(f"Product not found for ID: {product_id}")
            return jsonify({'message': 'Product not found'}), 404

        username_result = db.session.execute(
            "SELECT username FROM users WHERE id = :user_id",
            {"user_id": user_id}
        ).fetchone()
        if not username_result:
            logger.warning(f"User not found for ID: {user_id}")
            return jsonify({'message': 'User not found'}), 404

        product_name = product_name_result[0]
        username = username_result[0]

        result = db.session.execute(
            "EXEC DeleteProductReview @ProductName=:product_name, @Username=:username",
            {
                "product_name": product_name,
                "username": username
            }
        )
        row = result.fetchone()
        if row and row[0] == 'success':
            db.session.commit()
            logger.info(f"Review deleted for product {product_name} by user {username}")
            return jsonify({'message': row[2]}), 200
        else:
            db.session.rollback()
            logger.warning(f"Failed to delete review for product {product_name} by user {username}: {row[2] if row else 'No response'}")
            return jsonify({'message': row[2] if row else 'Error deleting review'}), 400

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"SQLAlchemy error deleting review: {str(e)}")
        return jsonify({'message': 'Error deleting review', 'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"General error deleting review: {str(e)}")
        return jsonify({'message': 'Error deleting review', 'error': str(e)}), 500
    
# ##########################################################################################################################################
@admin_bp.route('/admin/user/delete/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, user_id):
    # admin_user_id = 1  Temporary, it will change when we add the login
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for admin_user_id: {current_user.id}")
        return jsonify({'message': 'Unauthorized access'}), 403

    try:
        logger.debug(f"Attempting to delete user with ID: {user_id}")
        result = db.session.execute(
            "EXEC DeleteUser @UserID=:user_id",
            {"user_id": user_id}
        )
        row = result.fetchone()

        if row and row['status'] == 'success':
            db.session.commit()
            logger.info(f"User with ID {user_id} deleted successfully, orders and reviews preserved")
            return jsonify({'message': row['message']}), 200
        else:
            db.session.rollback()
            logger.warning(f"Failed to delete user with ID {user_id}: {row['message'] if row else 'No response from database'}")
            return jsonify({'message': row['message'] if row else 'Error deleting user'}), 400

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"SQLAlchemy error deleting user: {str(e)}")
        return jsonify({'message': 'Error deleting user', 'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"General error deleting user: {str(e)}")
        return jsonify({'message': 'Error deleting user', 'error': str(e)}), 500
# ##########################################################################################################################################

@admin_bp.route('/admin/user/<int:user_id>', methods=['GET'])
@token_required
def get_user(current_user, user_id):
    # admin_user_id = 1   Temporary, it will change when we add the login
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for admin_user_id: {current_user.id}")
        return jsonify({'message': 'Unauthorized access'}), 403

    try:
        logger.debug(f"Fetching profile for user with ID: {user_id}")
        result = db.session.execute(
            "EXEC GetUserProfile @UserID=:user_id",
            {"user_id": user_id}
        )
        row = result.fetchone()

        if not row:
            logger.warning(f"No user found for ID: {user_id}")
            return jsonify({'message': 'User not found'}), 404

        if row['status'] == 'fail':
            logger.warning(f"User not found for ID: {user_id}")
            return jsonify({'message': row['message']}), 404

        user = {
            "id": row[3],  # UserID
            "username": row[4],  # Username
            "full_name": row[5] or "",  # FullName
            "email": row[6] or "",  # Email
            "phone_number": row[7] or "",  # PhoneNumber
            "address": row[8] or "",  # Address
            "role": row[9]  # Role
        }

        logger.info(f"Retrieved profile for user with ID: {user_id}")
        return jsonify({'user': user}), 200

    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error fetching user: {str(e)}")
        return jsonify({'message': 'Error fetching user', 'error': str(e)}), 500
    except Exception as e:
        logger.error(f"General error fetching user: {str(e)}")
        return jsonify({'message': 'Error fetching user', 'error': str(e)}), 500
# ##########################################################################################################################################
@admin_bp.route('/admin/user/change-password/<int:user_id>', methods=['PUT'])
@token_required
def change_user_password(current_user, user_id):
    # admin_user_id = 1  Temporary, it will change when we add the login
    try:
        if not request.is_json:
            logger.error("Invalid JSON format in request")
            return jsonify({'message': 'Invalid JSON format'}), 400

        data = request.get_json(force=True)
        new_password = data.get('new_password')
        old_password = data.get('old_password') if 'old_password' in data else None

        if not new_password:
            logger.warning("New password not provided")
            return jsonify({'message': 'New password is required'}), 400

        # Check if requester is admin
        is_admin = check_admin(current_user)

        # If requester is not admin and changing their own password, validate old password
        if not is_admin and current_user.id == user_id:
            if not old_password:
                logger.warning("Old password not provided for self-password change")
                return jsonify({'message': 'Old password is required when changing your own password'}), 400

            user = User.query.get(user_id)
            if not user or not check_password_hash(user.pass_word, old_password):
                logger.warning(f"Invalid old password for user ID: {user_id}")
                return jsonify({'message': 'Old password is incorrect'}), 400
            
        # Hash the new password
        hashed_password = generate_password_hash(new_password)
        logger.debug(f"Changing password for user with ID: {user_id}")

        # Call stored procedure
        result = db.session.execute(
            "EXEC ChangePassword @RequesterID=:requester_id, @TargetUserID=:target_user_id, @NewPasswordHash=:new_password_hash",
            {
                "requester_id": current_user.id,
                "target_user_id": user_id,
                "new_password_hash": hashed_password
            }
        )
        row = result.fetchone()

        if row and row['status'] == 'success':
            db.session.commit()
            logger.info(f"Password changed successfully for user with ID: {user_id}")
            return jsonify({'message': row['message']}), 200
        else:
            db.session.rollback()
            logger.warning(f"Failed to change password for user with ID: {user_id}: {row['message'] if row else 'No response from database'}")
            return jsonify({'message': row['message'] if row else 'Error changing password'}), 400

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"SQLAlchemy error changing password: {str(e)}")
        return jsonify({'message': 'Error changing password', 'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"General error changing password: {str(e)}")
        return jsonify({'message': 'Error changing password', 'error': str(e)}), 500

# mahmoud