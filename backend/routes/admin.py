from flask import Blueprint, request, jsonify, current_app
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField
from wtforms.validators import DataRequired, NumberRange
from datetime import datetime
import uuid
import os
from werkzeug.utils import secure_filename
import logging
from sqlalchemy import text

# Import the correct models
from backend.models.Product import Product
from backend.models.Category import Category
from backend.models.User import User
from backend.extensions import db
from backend.routes.auth import token_required

# Setup logging
logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__)

# Check if user is admin
def check_admin(user):
    return user.user_role.lower() == 'admin'

class AddProductForm(FlaskForm):
    class Meta:
        csrf = False  

    product_name = StringField("Product Name", validators=[DataRequired()])
    description = StringField("Description")
    price = FloatField(
        "Price",
        validators=[
            DataRequired(),
            NumberRange(min=0.01, message="Price must be greater than 0"),
        ],
    )
    stock = IntegerField(
        "Stock",
        validators=[
            DataRequired(),
            NumberRange(min=0, message="Stock cannot be negative"),
        ],
    )
    category_id = IntegerField("Category ID", validators=[DataRequired()])
    image_url = StringField("Image URL")
    discount = FloatField(
        "Discount",
        validators=[
            NumberRange(min=0, max=100, message="Discount must be between 0 and 100"),
        ],
    )

class UpdatePriceForm(FlaskForm):
    class Meta:
        csrf = False

    new_price = FloatField(
        "New Price",
        validators=[
            DataRequired(),
            NumberRange(min=0.01, message="Price must be greater than 0"),
        ],
    )

class UpdateDiscountForm(FlaskForm):
    class Meta:
        csrf = False

    new_discount = FloatField(
        "New Discount",
        validators=[
            DataRequired(),
            NumberRange(min=0, max=100, message="Discount must be between 0 and 100"),
        ],
    )

@admin_bp.route("/admin/upload-image", methods=["POST"])
@token_required
def upload_image(current_user):
    if not check_admin(current_user):
        return jsonify({"message": "Unauthorized access"}), 403

    try:
        logger.info("Processing image upload request")

        if "image" not in request.files:
            logger.warning("No file part in request")
            return jsonify({"success": False, "message": "No file part"}), 400

        file = request.files["image"]

        if file.filename == "":
            logger.warning("No selected file")
            return jsonify({"success": False, "message": "No selected file"}), 400

        allowed_extensions = {"png", "jpg", "jpeg", "gif", "webp"}
        file_ext = (
            file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else ""
        )
        if file_ext not in allowed_extensions:
            logger.warning(f"Invalid file type: {file_ext}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
                    }
                ),
                400,
            )

        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}_{filename}"

        upload_folder = os.path.join(current_app.root_path, "static", "uploads")
        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        logger.info(f"File saved to {file_path}")

        image_url = f"/static/uploads/{unique_filename}"
        full_url = f"http://localhost:5000{image_url}"

        logger.info(f"Image URL: {image_url}")
        logger.info(f"Full URL: {full_url}")

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Image uploaded successfully",
                    "imageUrl": image_url,
                    "fullUrl": full_url,
                    "filename": unique_filename,
                }
            ),
            201,
        )

    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@admin_bp.route("/admin/upload", methods=["POST"])
@token_required
def upload_product_image(current_user):
    if not check_admin(current_user):
        return jsonify({"message": "Unauthorized access"}), 403

    try:
        logger.info("Processing product image upload request")

        if "image" not in request.files:
            logger.warning("No file part in request")
            return jsonify({"success": False, "message": "No file part"}), 400

        file = request.files["image"]
        product_name = request.form.get("product_name", "unknown_product")

        if file.filename == "":
            logger.warning("No selected file")
            return jsonify({"success": False, "message": "No selected file"}), 400

        allowed_extensions = {"png", "jpg", "jpeg", "gif", "webp"}
        file_ext = (
            file.filename.rsplit(".", 1)[1].lower() if "." in file.filename else ""
        )
        if file_ext not in allowed_extensions:
            logger.warning(f"Invalid file type: {file_ext}")
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
                    }
                ),
                400,
            )

        filename = secure_filename(file.filename)
        product_slug = secure_filename(product_name.lower().replace(" ", "-"))
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_filename = (
            f"{product_slug}_{timestamp}_{uuid.uuid4().hex[:8]}.{file_ext}"
        )

        upload_folder = os.path.join("static", "uploads")
        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        image_url = f"/static/uploads/{unique_filename}"
        full_url = f"http://localhost:5000{image_url}"

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Image uploaded successfully",
                    "productName": product_name,
                    "imageUrl": full_url,
                    "relativePath": image_url,
                    "filename": unique_filename,
                }
            ),
            201,
        )

    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@admin_bp.route("/admin", methods=["GET"])
@token_required
def admin_dashboard(current_user):
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({"message": "Unauthorized access"}), 403
    
    try:
        # Get product count
        product_count_query = text("SELECT COUNT(*) FROM products")
        product_count = db.session.execute(product_count_query).scalar() or 0
        
        # Get user count
        user_count_query = text("SELECT COUNT(*) FROM users")
        user_count = db.session.execute(user_count_query).scalar() or 0
        
        # Get order count and total revenue
        order_stats_query = text("""
            SELECT COUNT(*) as order_count, COALESCE(SUM(total_amount), 0) as total_revenue 
            FROM orders
        """)
        order_stats = db.session.execute(order_stats_query).fetchone()
        order_count = order_stats.order_count if order_stats else 0
        total_revenue = float(order_stats.total_revenue) if order_stats and order_stats.total_revenue else 0
        
        # Get recent activity (last 5 orders) - using TOP instead of LIMIT for SQL Server
        recent_activity_query = text("""
            SELECT TOP 5 o.id, o.user_id, u.username, o.order_date, o.total_amount, o.status
            FROM orders o
            JOIN users u ON o.user_id = u.id
            ORDER BY o.order_date DESC
        """)
        recent_activity_result = db.session.execute(recent_activity_query).fetchall()
        
        recent_activity = []
        for row in recent_activity_result:
            activity = {
                "id": row.id,
                "user_id": row.user_id,
                "username": row.username,
                "date": row.order_date.isoformat() if hasattr(row.order_date, 'isoformat') else str(row.order_date),
                "amount": float(row.total_amount) if row.total_amount else 0,
                "status": row.status
            }
            recent_activity.append(activity)
        
        return jsonify({
            "message": "Welcome to the admin dashboard",
            "stats": {
                "totalProducts": product_count,
                "totalUsers": user_count,
                "totalOrders": order_count,
                "totalRevenue": total_revenue
            },
            "recentActivity": recent_activity
        }), 200
        
    except Exception as e:
        logger.error(f"Error in admin dashboard: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"message": f"Error: {str(e)}"}), 500

@admin_bp.route("/admin/products", methods=["GET"])
@token_required
def admin_get_products(current_user):
    logger.info(f"Admin products request from user_id: {current_user.id}, role: {current_user.user_role}")
    
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({"message": "Unauthorized access"}), 403
    
    try:
        # First, check if we can execute a simple query
        logger.info("Testing database connection")
        test_query = text("SELECT 1")
        db.session.execute(test_query)
        logger.info("Database connection successful")
        
        # Now check if the products table exists - use SQL Server syntax
        logger.info("Checking if products table exists")
        table_check_query = text("""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_NAME = 'products'
        """)
        table_exists = db.session.execute(table_check_query).fetchone()
        
        if not table_exists:
            logger.error("Products table does not exist")
            return jsonify({
                "success": False,
                "message": "Products table does not exist in the database"
            }), 500
        
        logger.info("Products table exists, proceeding with query")
        
        # Continue with the original query...
        products_query = text("""
            SELECT p.*, c.category_name 
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            ORDER BY p.id DESC""")
        
        products_result = db.session.execute(products_query).fetchall()
        logger.info(f"Found {len(products_result) if products_result else 0} products")
        
        products = []
        for row in products_result:
            try:
                logger.debug(f"Processing product row: {row}")
                product = {
                    "id": row.id,
                    "product_name": row.product_name,
                    "description": row.product_description,
                    "price": float(row.price) if row.price is not None else 0.0,
                    "stock": row.stock if row.stock is not None else 0,
                    "category_id": row.category_id,
                    "category_name": row.category_name,
                    "image_url": row.image_url,
                    "is_active": bool(row.is_active) if hasattr(row, 'is_active') else True,
                    "discount": float(row.discount) if hasattr(row, 'discount') and row.discount is not None else 0.0
                }
                products.append(product)
            except Exception as row_error:
                logger.error(f"Error processing product row: {str(row_error)}")
                # Continue processing other rows
        
        logger.info(f"Returning {len(products)} products")
        return jsonify({"success": True, "products": products}), 200
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Error fetching products: {str(e)}")
        logger.error(error_traceback)
        # Return the error details in the response (only for debugging)
        return jsonify({
            "success": False, 
            "message": f"Error: {str(e)}",
            "traceback": error_traceback
        }), 500

@admin_bp.route("/admin/users", methods=["GET"])
@token_required
def admin_get_users(current_user):
    logger.info(f"Admin users request from user_id: {current_user.id}, role: {current_user.user_role}")
    
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({"message": "Unauthorized access"}), 403
    
    try:
        # First, check if we can execute a simple query
        logger.info("Testing database connection")
        test_query = text("SELECT 1")
        db.session.execute(test_query)
        logger.info("Database connection successful")
        
        # Now check if the users table exists - use SQL Server syntax
        logger.info("Checking if users table exists")
        try:
            table_check_query = text("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_NAME = 'users'
            """)
            table_exists = db.session.execute(table_check_query).fetchone()
            
            if not table_exists:
                logger.error("Users table does not exist")
                return jsonify({
                    "success": False,
                    "message": "Users table does not exist in the database"
                }), 500
                
            logger.info("Users table exists, proceeding with query")
        except Exception as table_check_error:
            logger.error(f"Error checking users table: {str(table_check_error)}")
            # Try a simpler approach - just query the users table directly
            logger.info("Trying alternative approach to check users table")
        
        # Try a simpler query that works across different SQL dialects
        try:
            # Get all users from the database with a simpler query
            users_query = text("SELECT * FROM users")
            users_result = db.session.execute(users_query).fetchall()
            logger.info(f"Found {len(users_result) if users_result else 0} users")
            
            users = []
            for row in users_result:
                try:
                    # Get column names dynamically
                    columns = row._mapping.keys()
                    logger.debug(f"Available columns: {columns}")
                    
                    user = {
                        "id": row.id if 'id' in columns else None,
                        "username": row.username if 'username' in columns else None,
                        "email": row.email if 'email' in columns else None,
                        "full_name": row.full_name if 'full_name' in columns else None,
                        "user_address": row.user_address if hasattr(row, 'user_address') else None,
                        "phone_number": row.phone_number if hasattr(row, 'phone_number') else None,
                        "user_role": row.user_role if 'user_role' in columns else None
                    }
                    
                    # Add these fields only if they exist
                    if hasattr(row, 'created_at'):
                        user["created_at"] = row.created_at.isoformat() if hasattr(row.created_at, 'isoformat') else str(row.created_at)
                    
                    if hasattr(row, 'last_login') and row.last_login:
                        user["last_login"] = row.last_login.isoformat() if hasattr(row.last_login, 'isoformat') else str(row.last_login)
                    
                    users.append(user)
                except Exception as row_error:
                    logger.error(f"Error processing user row: {str(row_error)}")
                    # Continue processing other rows
            
            logger.info(f"Returning {len(users)} users")
            return jsonify({"success": True, "users": users}), 200
            
        except Exception as query_error:
            logger.error(f"Error executing users query: {str(query_error)}")
            return jsonify({
                "success": False,
                "message": f"Database query error: {str(query_error)}"
            }), 500
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Error fetching users: {str(e)}")
        logger.error(error_traceback)
        return jsonify({
            "success": False, 
            "message": f"Error: {str(e)}",
            "traceback": error_traceback
        }), 500

@admin_bp.route("/admin/product/toggle-visibility/<int:product_id>", methods=["POST"])
@token_required
def toggle_product_visibility(current_user, product_id):
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({"message": "Unauthorized access"}), 403
    
    if not request.is_json:
        logger.error("Invalid JSON format in request")
        return jsonify({"message": "Invalid JSON format"}), 400
    
    data = request.get_json()
    is_active = data.get('is_active')
    
    if is_active is None:
        return jsonify({"message": "is_active field is required"}), 400
    
    try:
        
        product_result = db.session.execute(
            text("SELECT product_name FROM products WHERE id = :product_id"),
            {"product_id": product_id}
        ).fetchone()
        
        if not product_result:
            logger.warning(f"Product not found for ID: {product_id}")
            return jsonify({"message": "Product not found"}), 404
        
        
        update_query = text("""
            UPDATE products 
            SET is_active = :is_active
            WHERE id = :product_id""")
        
        db.session.execute(
            update_query,
            {
                "product_id": product_id,
                "is_active": is_active
            }
        )
        
        db.session.commit()
        logger.info(f"Product {product_id} visibility updated to {is_active}")
        return jsonify({"message": "Product visibility updated successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating product visibility: {str(e)}")
        return jsonify({"message": "Error updating product visibility", "error": str(e)}), 500

@admin_bp.route("/admin/product/update/<int:product_id>", methods=["POST"])
@token_required
def update_product(current_user, product_id):
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({"message": "Unauthorized access"}), 403
    
    if not request.is_json:
        logger.error("Invalid JSON format in request")
        return jsonify({"message": "Invalid JSON format"}), 400
    
    data = request.get_json()
    
    try:
        
        product_result = db.session.execute(
            text("SELECT * FROM products WHERE id = :product_id"),
            {"product_id": product_id}
        ).fetchone()
        
        if not product_result:
            logger.warning(f"Product not found for ID: {product_id}")
            return jsonify({"message": "Product not found"}), 404
        
        
        update_query = text("""
            UPDATE products 
            SET product_name = :product_name,
                product_description = :description,
                price = :price,
                stock = :stock,
                category_id = :category_id,
                image_url = :image_url,
                discount = :discount
            WHERE id = :product_id""")
        
        db.session.execute(
            update_query,
            {
                "product_id": product_id,
                "product_name": data.get("product_name"),
                "description": data.get("description"),
                "price": data.get("price"),
                "stock": data.get("stock"),
                "category_id": data.get("category_id"),
                "image_url": data.get("image_url"),
                "discount": data.get("discount", 0)
            }
        )
        
        db.session.commit()
        logger.info(f"Product {product_id} updated successfully")
        return jsonify({"success": True, "message": "Product updated successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating product: {str(e)}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@admin_bp.route("/admin/user/delete/<int:user_id>", methods=["DELETE"])
@token_required
def delete_user(current_user, user_id):
    logger.info(f"Delete user request for user_id: {user_id} from admin: {current_user.id}")
    
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({"message": "Unauthorized access"}), 403
    
    try:
        # Check if the user exists
        user_check_query = text("SELECT id, username, user_role FROM users WHERE id = :user_id")
        user = db.session.execute(user_check_query, {"user_id": user_id}).fetchone()
        
        if not user:
            logger.warning(f"User not found: {user_id}")
            return jsonify({"success": False, "message": "User not found"}), 404
        
        # Prevent deletion of admin users
        if user.user_role == 'Admin':
            logger.warning(f"Attempt to delete admin user: {user_id}")
            return jsonify({"success": False, "message": "Cannot delete admin users"}), 403
        
        # First, delete related records to maintain referential integrity
        # The order matters due to foreign key constraints
        
        # 1. First delete from cart_details (child table)
        cart_details_query = text("""
            DELETE FROM cart_details 
            WHERE cart_id IN (SELECT id FROM cart WHERE user_id = :user_id)
        """)
        db.session.execute(cart_details_query, {"user_id": user_id})
        
        # 2. Then delete from cart (parent table)
        cart_query = text("DELETE FROM cart WHERE user_id = :user_id")
        db.session.execute(cart_query, {"user_id": user_id})
        
        # 3. Delete from wishlist (if exists)
        try:
            wishlist_query = text("DELETE FROM wishlist WHERE user_id = :user_id")
            db.session.execute(wishlist_query, {"user_id": user_id})
        except Exception as e:
            logger.warning(f"Error deleting from wishlist (may not exist): {str(e)}")
        
        # 4. Delete from product_reviews
        reviews_query = text("DELETE FROM product_reviews WHERE user_id = :user_id")
        db.session.execute(reviews_query, {"user_id": user_id})
        
        # 5. Delete from order_details first
        order_details_query = text("""
            DELETE FROM order_details 
            WHERE order_id IN (SELECT id FROM orders WHERE user_id = :user_id)
        """)
        db.session.execute(order_details_query, {"user_id": user_id})
        
        # 6. Then delete from orders
        orders_query = text("DELETE FROM orders WHERE user_id = :user_id")
        db.session.execute(orders_query, {"user_id": user_id})
        
        # 7. Finally, delete the user
        user_query = text("DELETE FROM users WHERE id = :user_id")
        db.session.execute(user_query, {"user_id": user_id})
        
        # Commit all changes
        db.session.commit()
        
        logger.info(f"User {user_id} ({user.username}) completely deleted from database")
        return jsonify({
            "success": True, 
            "message": f"User {user.username} deleted successfully"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Error deleting user: {str(e)}")
        logger.error(error_traceback)
        return jsonify({
            "success": False, 
            "message": f"Error: {str(e)}",
            "traceback": error_traceback
        }), 500

@admin_bp.route("/admin/user/update/<int:user_id>", methods=["PUT", "POST"])
@token_required
def update_user(current_user, user_id):
    logger.info(f"Update user request for user_id: {user_id} from admin: {current_user.id}")
    
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({"message": "Unauthorized access"}), 403
    
    if not request.is_json:
        logger.error("Invalid JSON format in request")
        return jsonify({"message": "Invalid JSON format"}), 400
    
    data = request.get_json()
    
    try:
        # Check if the user exists
        user_check_query = text("SELECT id, username FROM users WHERE id = :user_id")
        user = db.session.execute(user_check_query, {"user_id": user_id}).fetchone()
        
        if not user:
            logger.warning(f"User not found: {user_id}")
            return jsonify({"success": False, "message": "User not found"}), 404
        
        # Prepare update fields
        update_fields = []
        params = {"user_id": user_id}
        
        # Add fields to update if they exist in the request
        if "username" in data and data["username"]:
            update_fields.append("username = :username")
            params["username"] = data["username"]
        
        if "email" in data and data["email"]:
            update_fields.append("email = :email")
            params["email"] = data["email"]
        
        if "full_name" in data and data["full_name"]:
            update_fields.append("full_name = :full_name")
            params["full_name"] = data["full_name"]
        
        if "user_address" in data:
            update_fields.append("user_address = :user_address")
            params["user_address"] = data["user_address"]
        
        if "phone_number" in data:
            update_fields.append("phone_number = :phone_number")
            params["phone_number"] = data["phone_number"]
        
        if "user_role" in data and data["user_role"]:
            update_fields.append("user_role = :user_role")
            params["user_role"] = data["user_role"]
        
        # Handle password update separately (only if provided)
        if "password" in data and data["password"]:
            # Hash the password
            hashed_password = generate_password_hash(data["password"])
            update_fields.append("password_hash = :password_hash")
            params["password_hash"] = hashed_password
        
        # If no fields to update, return early
        if not update_fields:
            return jsonify({"success": True, "message": "No changes to update"}), 200
        
        # Build and execute the update query
        update_query = text(f"""
            UPDATE users 
            SET {', '.join(update_fields)}
            WHERE id = :user_id
        """)
        
        db.session.execute(update_query, params)
        db.session.commit()
        
        logger.info(f"User {user_id} ({user.username}) updated successfully")
        return jsonify({
            "success": True, 
            "message": f"User {user.username} updated successfully"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Error updating user: {str(e)}")
        logger.error(error_traceback)
        return jsonify({
            "success": False, 
            "message": f"Error: {str(e)}",
            "traceback": error_traceback
        }), 500

@admin_bp.route("/admin/product/add", methods=["POST"])
@token_required
def add_product(current_user):
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({"success": False, "message": "Unauthorized access"}), 403
    
    try:
        if not request.is_json:
            logger.error("Invalid JSON format in request")
            return jsonify({"success": False, "message": "Invalid JSON format"}), 400
        
        data = request.get_json()
        logger.info(f"Received product data: {data}")
        
        # Basic validation
        required_fields = ['product_name', 'price', 'stock', 'category_id']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    "success": False, 
                    "message": f"Missing required field: {field}"
                }), 400
        
        # Create a new product
        new_product = Product(
            product_name=data.get("product_name"),
            product_description=data.get("description", ""),  # Changed to product_description
            price=data.get("price"),
            stock=data.get("stock"),
            category_id=data.get("category_id"),
            image_url=data.get("image_url", ""),
            discount=data.get("discount", 0),
            is_active=True
        )
        
        db.session.add(new_product)
        db.session.commit()
        
        logger.info(f"Product created successfully: {new_product.id}")
        
        # Return the newly created product
        return jsonify({
            "success": True, 
            "message": "Product added successfully",
            "product": {
                "id": new_product.id,
                "product_name": new_product.product_name,
                "description": new_product.product_description,  # Changed to product_description
                "price": float(new_product.price),
                "stock": new_product.stock,
                "category_id": new_product.category_id,
                "image_url": new_product.image_url,
                "discount": float(new_product.discount),
                "is_active": new_product.is_active
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding product: {str(e)}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500
