from flask import Blueprint, request, jsonify, current_app
from backend.extensions import db
from backend.models import User, Product
import json
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField
from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
    Regexp,
    ValidationError,
)
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from decimal import Decimal
from backend.routes.auth import token_required
import os
from werkzeug.utils import secure_filename
import uuid
import jwt
from datetime import datetime

admin_bp = Blueprint("admin", __name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def check_admin(current_user):
    return current_user.user_role.lower() == "admin"

def parse_json_result(result):
    if result and result[0][0]:
        try:
            return json.loads(result[0][0])
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON data: {str(e)}")
            return []
    return []

# Form classes
class AddProductForm(FlaskForm):
    class Meta:
        csrf = False  # Disable CSRF for API

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
        response_data = {
            "message": "Welcome to the admin dashboard",
            "stats": {
                "totalProducts": 0,
                "totalUsers": 0,
                "totalOrders": 0,
                "totalRevenue": 0
            },
            "recentActivity": []
        }
        
        # Get product count
        try:
            product_count_result = db.session.execute(text("SELECT COUNT(*) FROM products")).scalar()
            product_count = int(product_count_result) if product_count_result is not None else 0
            response_data["stats"]["totalProducts"] = product_count
            logger.info(f"Product count: {product_count}")
        except Exception as e:
            logger.error(f"Error getting product count: {str(e)}")
            try:
                from sqlalchemy import text
                product_count_result = db.session.execute(text("SELECT COUNT(*) FROM products")).scalar()
                product_count = int(product_count_result) if product_count_result is not None else 0
                response_data["stats"]["totalProducts"] = product_count
                logger.info(f"Product count (alternative method): {product_count}")
            except Exception as inner_e:
                logger.error(f"Error getting product count with alternative method: {str(inner_e)}")
        
        # Get user count
        try:
            user_count_result = db.session.execute(text("SELECT COUNT(*) FROM users")).scalar()
            user_count = int(user_count_result) if user_count_result is not None else 0
            response_data["stats"]["totalUsers"] = user_count
            logger.info(f"User count: {user_count}")
        except Exception as e:
            logger.error(f"Error getting user count: {str(e)}")
        
        # Get order count and revenue
        try:
            order_count_result = db.session.execute(text("SELECT COUNT(*) FROM orders")).scalar()
            order_count = int(order_count_result) if order_count_result is not None else 0
            response_data["stats"]["totalOrders"] = order_count
            logger.info(f"Order count: {order_count}")
            
            revenue_result = db.session.execute(text("SELECT COALESCE(SUM(total_price), 0) FROM orders")).scalar()
            total_revenue = float(revenue_result) if revenue_result is not None else 0
            response_data["stats"]["totalRevenue"] = total_revenue
            logger.info(f"Total revenue: {total_revenue}")
        except Exception as e:
            logger.error(f"Error getting order stats: {str(e)}")
        
        # Get recent activity
        try:
            # Get recent orders
            recent_orders_query = text("""
                SELECT o.id, o.total_price, o.created_at, u.username 
                FROM orders o
                JOIN users u ON o.user_id = u.id
                ORDER BY o.created_at DESC
                LIMIT 5
            """)
            recent_orders_result = db.session.execute(recent_orders_query)
            
            for row in recent_orders_result:
                order_id, total_price, created_at, username = row
                response_data["recentActivity"].append({
                    "type": "New Order",
                    "description": f"Order #{order_id} placed by {username} for ${float(total_price) if total_price else 0:.2f}",
                    "timestamp": created_at.isoformat() if created_at else datetime.now().isoformat()
                })
                
            # Get recent users
            recent_users_query = text("""
                SELECT id, username, created_at
                FROM users
                ORDER BY created_at DESC
                LIMIT 3
            """)
            recent_users_result = db.session.execute(recent_users_query)
            
            for row in recent_users_result:
                user_id, username, created_at = row
                response_data["recentActivity"].append({
                    "type": "New User",
                    "description": f"User {username} joined",
                    "timestamp": created_at.isoformat() if created_at else datetime.now().isoformat()
                })
                
            # Sort all activities by timestamp
            response_data["recentActivity"] = sorted(
                response_data["recentActivity"],
                key=lambda x: x["timestamp"],
                reverse=True
            )
        except Exception as e:
            logger.error(f"Error getting recent activity: {str(e)}")
        
        return jsonify(response_data), 200
        
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"SQLAlchemy error fetching dashboard stats: {str(e)}")
        return (
            jsonify(
                {"message": "Error fetching dashboard statistics", "error": str(e)}
            ),
            500,
        )
    except Exception as e:
        logger.error(f"General error fetching dashboard stats: {str(e)}")
        return (
            jsonify(
                {"message": "Error fetching dashboard statistics", "error": str(e)}
            ),
            500,
        )

@admin_bp.route("/admin/products", methods=["GET"])
@token_required
def get_admin_products(current_user):
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({"message": "Unauthorized access"}), 403

    try:
        logger.debug("Fetching all products for admin dashboard")
        
        # Use a direct SQL query instead of stored procedure
        query = text("""
            SELECT p.id, p.product_name, p.product_description, p.price, p.stock, 
                   p.category_id, c.category_name, p.image_url, p.discount, p.is_active
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            ORDER BY p.id
        """)
        
        result = db.session.execute(query)
        products = result.fetchall()

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
                "image_url": row[7] if row[7] else "",
                "discount": float(row[8]) if isinstance(row[8], Decimal) else row[8],
                "is_active": row[9] if len(row) > 9 else True,
            })

        logger.info(f"Retrieved {len(formatted_products)} products for admin dashboard")
        return jsonify({"products": formatted_products}), 200
        
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error fetching products: {str(e)}")
        return jsonify({"message": "Error fetching products", "error": str(e)}), 500
    except Exception as e:
        logger.error(f"General error fetching products: {str(e)}")
        return jsonify({"message": "Error fetching products", "error": str(e)}), 500

@admin_bp.route("/admin/product/add", methods=["POST"])
@token_required
def add_product(current_user):
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({"message": "Unauthorized access"}), 403

    if not request.is_json:
        logger.error("Invalid JSON format in request")
        return jsonify({"message": "Invalid JSON format"}), 400

    form = AddProductForm(data=request.get_json(force=True))

    if not form.validate():
        errors = {field.name: field.errors for field in form}
        logger.debug(f"Validation errors: {errors}")
        return jsonify({"message": "Validation error", "errors": errors}), 400

    try:
        # Use direct SQL insert instead of stored procedure
        query = text("""
            INSERT INTO products (product_name, product_description, price, stock, category_id, image_url, discount, is_active)
            VALUES (:product_name, :description, :price, :stock, :category_id, :image_url, :discount, 1)
            RETURNING id
        """)
        
        result = db.session.execute(
            query,
            {
                "product_name": form.product_name.data,
                "description": form.description.data or "",
                "price": form.price.data,
                "stock": form.stock.data,
                "category_id": form.category_id.data,
                "image_url": form.image_url.data or "",
                "discount": form.discount.data or 0.0,
            },
        )
        
        new_product_id = result.scalar()
        
        if new_product_id:
            db.session.commit()
            logger.info(f"Product {form.product_name.data} added successfully with ID {new_product_id}")
            return jsonify({"message": "Product added successfully", "product_id": new_product_id}), 201
        else:
            db.session.rollback()
            logger.error("Error adding product: No ID returned")
            return jsonify({"message": "Error adding product: No ID returned"}), 500

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"SQLAlchemy error adding product: {str(e)}")
        return jsonify({"message": "Error adding product", "error": str(e)}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"General error adding product: {str(e)}")
        return jsonify({"message": "Error adding product", "error": str(e)}), 500

@admin_bp.route("/admin/product/delete/<int:product_id>", methods=["DELETE"])
@token_required
def delete_product(current_user, product_id):
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({"message": "Unauthorized access"}), 403
    
    try:
        # Check if product exists
        product_result = db.session.execute(
            text("SELECT product_name FROM products WHERE id = :product_id"),
            {"product_id": product_id}
        ).fetchone()
        
        if not product_result:
            logger.warning(f"Product not found for ID: {product_id}")
            return jsonify({"message": "Product not found"}), 404
        
        product_name = product_result[0]
        
        # Delete product
        delete_query = text("""
            DELETE FROM products 
            WHERE id = :product_id
        """)
        
        db.session.execute(
            delete_query,
            {"product_id": product_id}
        )
        
        db.session.commit()
        logger.info(f"Product {product_name} deleted successfully")
        return jsonify({"message": f"Product {product_name} deleted successfully"}), 200
            
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"SQLAlchemy error deleting product: {str(e)}")
        return jsonify({"message": "Error deleting product", "error": str(e)}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"General error deleting product: {str(e)}")
        return jsonify({"message": "Error deleting product", "error": str(e)}), 500

@admin_bp.route("/admin/product/update-price/<int:product_id>", methods=["POST"])
@token_required
def update_product_price(current_user, product_id):
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({"message": "Unauthorized access"}), 403

    if not request.is_json:
        logger.error("Invalid JSON format in request")
        return jsonify({"message": "Invalid JSON format"}), 400

    form = UpdatePriceForm(data=request.get_json(force=True))

    if not form.validate():
        errors = {field.name: field.errors for field in form}
        logger.debug(f"Validation errors: {errors}")
        return jsonify({"message": "Validation error", "errors": errors}), 400

    
    product_name_result = db.session.execute(
        "SELECT product_name FROM products WHERE id = :product_id",
        {"product_id": product_id},
    ).fetchone()

    if not product_name_result:
        logger.warning(f"Product not found for ID: {product_id}")
        return jsonify({"message": "Product not found"}), 404

    product_name = product_name_result[0]

    try:
        query = text(
        )
        result = db.session.execute(
            query, {"product_name": product_name, "new_price": form.new_price.data}
        )

        logger.debug("Fetching result...")
        row = result.fetchone()
        if row:
            status = row["status"]
            message = row["message"]
            logger.debug(f"Status: {status}, Message: {message}")
            if status == "success":
                db.session.commit()
                logger.info(f"Price updated for product {product_name}")
                return jsonify({"message": message}), 200
            else:
                db.session.rollback()
                return jsonify({"message": message}), 400
        else:
            db.session.rollback()
            logger.error("Error updating price: No response from database")
            return (
                jsonify({"message": "Error updating price: No response from database"}),
                500,
            )

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"SQLAlchemy error updating price: {str(e)}")
        return jsonify({"message": "Error updating price", "error": str(e)}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"General error updating price: {str(e)}")
        return jsonify({"message": "Error updating price", "error": str(e)}), 500





@admin_bp.route("/admin/product/update-discount/<int:product_id>", methods=["POST"])
@token_required
def update_product_discount(current_user, product_id):
    
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({"message": "Unauthorized access"}), 403

    if not request.is_json:
        logger.error("Invalid JSON format in request")
        return jsonify({"message": "Invalid JSON format"}), 400

    form = UpdateDiscountForm(data=request.get_json(force=True))

    if not form.validate():
        errors = {field.name: field.errors for field in form}
        logger.debug(f"Validation errors: {errors}")
        return jsonify({"message": "Validation error", "errors": errors}), 400

    
    product_name_result = db.session.execute(
        "SELECT product_name FROM products WHERE id = :product_id",
        {"product_id": product_id},
    ).fetchone()

    if not product_name_result:
        logger.warning(f"Product not found for ID: {product_id}")
        return jsonify({"message": "Product not found"}), 404

    product_name = product_name_result[0]

    try:
        query = text(
        )
        result = db.session.execute(
            query,
            {"product_name": product_name, "new_discount": form.new_discount.data},
        )

        logger.debug("Fetching result...")
        row = result.fetchone()
        if row:
            status = row["status"]
            message = row["message"]
            logger.debug(f"Status: {status}, Message: {message}")
            if status == "success":
                db.session.commit()
                logger.info(f"Discount updated for product {product_name}")
                return jsonify({"message": message}), 200
            else:
                db.session.rollback()
                return jsonify({"message": message}), 400
        else:
            db.session.rollback()
            logger.error("Error updating discount: No response from database")
            return (
                jsonify(
                    {"message": "Error updating discount: No response from database"}
                ),
                500,
            )

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"SQLAlchemy error updating discount: {str(e)}")
        return jsonify({"message": "Error updating discount", "error": str(e)}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"General error updating discount: {str(e)}")
        return jsonify({"message": "Error updating discount", "error": str(e)}), 500





@admin_bp.route("/admin/orders", methods=["GET"])
@token_required
def manage_orders(current_user):
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({"message": "Unauthorized access"}), 403

    try:
        logger.debug("Fetching orders...")
        
        # Use direct SQL query instead of stored procedure
        query = text("""
            SELECT o.id, o.user_id, u.username, u.full_name, u.user_address, 
                   u.phone_number, o.total_price, o.status, o.created_at
            FROM orders o
            JOIN users u ON o.user_id = u.id
            ORDER BY o.created_at DESC
        """)
        
        result = db.session.execute(query)
        
        formatted_orders = []
        for row in result:
            formatted_orders.append({
                "id": row[0],
                "user_id": row[1],
                "username": row[2],
                "full_name": row[3],
                "user_address": row[4],
                "phone_number": row[5],
                "total_amount": float(row[6]) if isinstance(row[6], Decimal) else row[6],
                "status": row[7],
                "order_date": str(row[8]),
            })
        
        logger.info(f"Found {len(formatted_orders)} orders")
        return jsonify({"orders": formatted_orders}), 200

    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error fetching orders: {str(e)}")
        return jsonify({"message": "Error fetching orders", "error": str(e)}), 500
    except Exception as e:
        logger.error(f"General error fetching orders: {str(e)}")
        return jsonify({"message": "Error fetching orders", "error": str(e)}), 500




@admin_bp.route("/admin/order/<int:order_id>", methods=["GET"])
@token_required
def get_order_details(current_user, order_id):
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({"message": "Unauthorized access"}), 403

    try:
        logger.debug(f"Fetching details for order ID: {order_id}")
        
        # Get order details
        order_query = text("""
            SELECT o.id, o.user_id, u.username, u.full_name, u.user_address, 
                   u.phone_number, o.total_price, o.status, o.created_at
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE o.id = :order_id
        """)
        
        order_result = db.session.execute(order_query, {"order_id": order_id})
        order_data = order_result.fetchone()
        
        if not order_data:
            logger.warning(f"Order not found for ID: {order_id}")
            return jsonify({"message": "Order not found"}), 404
        
        # Get order items
        items_query = text("""
            SELECT p.id, p.product_name, oi.quantity, oi.price, (oi.quantity * oi.price) as subtotal, p.image_url
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = :order_id
        """)
        
        items_result = db.session.execute(items_query, {"order_id": order_id})
        
        order_items = []
        for item in items_result:
            order_items.append({
                "product_id": item[0],
                "product_name": item[1],
                "quantity": item[2],
                "price": float(item[3]) if isinstance(item[3], Decimal) else item[3],
                "subtotal": float(item[4]) if isinstance(item[4], Decimal) else item[4],
                "image_url": item[5] if len(item) > 5 else None
            })
        
        order_details = {
            "id": order_data[0],
            "user_id": order_data[1],
            "username": order_data[2],
            "full_name": order_data[3],
            "user_address": order_data[4],
            "phone_number": order_data[5],
            "total_amount": float(order_data[6]) if isinstance(order_data[6], Decimal) else order_data[6],
            "status": order_data[7],
            "order_date": str(order_data[8]),
            "items": order_items
        }
        
        return jsonify({"order": order_details}), 200
        
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error fetching order details: {str(e)}")
        return jsonify({"message": "Error fetching order details", "error": str(e)}), 500
    except Exception as e:
        logger.error(f"General error fetching order details: {str(e)}")
        return jsonify({"message": "Error fetching order details", "error": str(e)}), 500


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
        return jsonify({"message": "Missing is_active parameter"}), 400
    
    try:
        # Check if product exists
        product_result = db.session.execute(
            text("SELECT product_name FROM products WHERE id = :product_id"),
            {"product_id": product_id}
        ).fetchone()
        
        if not product_result:
            logger.warning(f"Product not found for ID: {product_id}")
            return jsonify({"message": "Product not found"}), 404
        
        product_name = product_result[0]
        
        # Update product visibility
        update_query = text("""
            UPDATE products 
            SET is_active = :is_active 
            WHERE id = :product_id
        """)
        
        db.session.execute(
            update_query,
            {"product_id": product_id, "is_active": is_active}
        )
        
        db.session.commit()
        logger.info(f"Visibility updated for product {product_name} to {is_active}")
        return jsonify({"message": "Product visibility updated successfully", "is_active": is_active}), 200
            
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"SQLAlchemy error updating product visibility: {str(e)}")
        return jsonify({"message": "Error updating product visibility", "error": str(e)}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"General error updating product visibility: {str(e)}")
        return jsonify({"message": "Error updating product visibility", "error": str(e)}), 500

@admin_bp.route("/admin/users", methods=["GET"])
@token_required
def get_admin_users(current_user):
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({"message": "Unauthorized access"}), 403

    try:
        logger.debug("Fetching all users for admin dashboard")
        
        # Use a direct SQL query to get all users except the current admin
        query = text("""
            SELECT id, username, email, full_name, user_address, phone_number, user_role
            FROM users
            ORDER BY id
        """)
        
        result = db.session.execute(query)
        users = result.fetchall()

        formatted_users = []
        for row in users:
            # Skip the deleted_user placeholder account from the results
            if row[1] == 'deleted_user':
                continue
                
            formatted_users.append({
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "full_name": row[3],
                "user_address": row[4] or "",
                "phone_number": row[5] or "",
                "user_role": row[6]
            })

        logger.info(f"Retrieved {len(formatted_users)} users for admin dashboard")
        return jsonify({"users": formatted_users}), 200
        
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error fetching users: {str(e)}")
        return jsonify({"message": "Error fetching users", "error": str(e)}), 500
    except Exception as e:
        logger.error(f"General error fetching users: {str(e)}")
        return jsonify({"message": "Error fetching users", "error": str(e)}), 500

@admin_bp.route("/admin/user/<int:user_id>", methods=["GET"])
@token_required
def get_user_details(current_user, user_id):
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({"message": "Unauthorized access"}), 403

    try:
        logger.debug(f"Fetching details for user ID: {user_id}")
        
        # Get user details
        user_query = text("""
            SELECT id, username, email, full_name, user_address, phone_number, user_role
            FROM users
            WHERE id = :user_id
        """)
        
        user_result = db.session.execute(user_query, {"user_id": user_id})
        user_data = user_result.fetchone()
        
        if not user_data:
            logger.warning(f"User not found for ID: {user_id}")
            return jsonify({"message": "User not found"}), 404
        
        # Get user's orders
        orders_query = text("""
            SELECT id, total_price, status, created_at
            FROM orders
            WHERE user_id = :user_id
            ORDER BY created_at DESC
        """)
        
        orders_result = db.session.execute(orders_query, {"user_id": user_id})
        
        user_orders = []
        for order in orders_result:
            user_orders.append({
                "id": order[0],
                "total_amount": float(order[1]) if isinstance(order[1], Decimal) else order[1],
                "status": order[2],
                "order_date": str(order[3])
            })
        
        user_details = {
            "id": user_data[0],
            "username": user_data[1],
            "email": user_data[2],
            "full_name": user_data[3],
            "user_address": user_data[4] or "",
            "phone_number": user_data[5] or "",
            "user_role": user_data[6],
            "orders": user_orders
        }
        
        return jsonify({"user": user_details}), 200
        
    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error fetching user details: {str(e)}")
        return jsonify({"message": "Error fetching user details", "error": str(e)}), 500
    except Exception as e:
        logger.error(f"General error fetching user details: {str(e)}")
        return jsonify({"message": "Error fetching user details", "error": str(e)}), 500

@admin_bp.route("/admin/user/update/<int:user_id>", methods=["PUT"])
@token_required
def update_user(current_user, user_id):
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({"message": "Unauthorized access"}), 403
    
    if not request.is_json:
        logger.error("Invalid JSON format in request")
        return jsonify({"message": "Invalid JSON format"}), 400
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ["username", "email", "full_name"]
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"message": f"Missing required field: {field}"}), 400
    
    try:
        # Check if user exists
        user_result = db.session.execute(
            text("SELECT username FROM users WHERE id = :user_id"),
            {"user_id": user_id}
        ).fetchone()
        
        if not user_result:
            logger.warning(f"User not found for ID: {user_id}")
            return jsonify({"message": "User not found"}), 404
        
        # Check if username is already taken by another user
        if data.get("username") != user_result[0]:
            username_check = db.session.execute(
                text("SELECT id FROM users WHERE username = :username AND id != :user_id"),
                {"username": data["username"], "user_id": user_id}
            ).fetchone()
            
            if username_check:
                return jsonify({"message": "Username already taken"}), 400
        
        # Check if email is already taken by another user
        email_check = db.session.execute(
            text("SELECT id FROM users WHERE email = :email AND id != :user_id"),
            {"email": data["email"], "user_id": user_id}
        ).fetchone()
        
        if email_check:
            return jsonify({"message": "Email already taken"}), 400
        
        # Update user
        update_query = text("""
            UPDATE users 
            SET username = :username, 
                email = :email, 
                full_name = :full_name, 
                user_address = :user_address, 
                phone_number = :phone_number,
                user_role = :user_role
            WHERE id = :user_id
        """)
        
        db.session.execute(
            update_query,
            {
                "user_id": user_id,
                "username": data["username"],
                "email": data["email"],
                "full_name": data["full_name"],
                "user_address": data.get("user_address", ""),
                "phone_number": data.get("phone_number", ""),
                "user_role": data.get("user_role", "Customer")
            }
        )
        
        # Update password if provided
        if "password" in data and data["password"]:
            password_hash = generate_password_hash(data["password"])
            
            password_query = text("""
                UPDATE users 
                SET pass_word = :password
                WHERE id = :user_id
            """)
            
            db.session.execute(
                password_query,
                {"user_id": user_id, "password": password_hash}
            )
        
        db.session.commit()
        logger.info(f"User {data['username']} updated successfully")
        return jsonify({"message": "User updated successfully"}), 200
            
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"SQLAlchemy error updating user: {str(e)}")
        return jsonify({"message": "Error updating user", "error": str(e)}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"General error updating user: {str(e)}")
        return jsonify({"message": "Error updating user", "error": str(e)}), 500

@admin_bp.route("/admin/user/delete/<int:user_id>", methods=["DELETE"])
@token_required
def delete_user(current_user, user_id):
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({"message": "Unauthorized access"}), 403
    
    try:
        # Check if user exists
        user_result = db.session.execute(
            text("SELECT username, user_role FROM users WHERE id = :user_id"),
            {"user_id": user_id}
        ).fetchone()
        
        if not user_result:
            logger.warning(f"User not found for ID: {user_id}")
            return jsonify({"message": "User not found"}), 404
        
        username, user_role = user_result
        
        # Prevent deletion of admin users
        if user_role == "Admin":
            logger.warning(f"Attempt to delete admin user: {username}")
            return jsonify({"message": "Cannot delete admin users"}), 403
        
        # Prevent self-deletion
        if user_id == current_user.id:
            logger.warning(f"User attempted to delete themselves: {username}")
            return jsonify({"message": "Cannot delete your own account"}), 403
        
        logger.debug(f"Completely deleting user {username} (ID: {user_id}) and all associated data")
        
        # Delete user's reviews
        try:
            delete_reviews_query = text("""
                DELETE FROM product_reviews
                WHERE user_id = :user_id
            """)
            
            result = db.session.execute(
                delete_reviews_query,
                {"user_id": user_id}
            )
            logger.debug(f"Deleted user's reviews")
        except Exception as e:
            logger.error(f"Error deleting reviews: {str(e)}")
            return jsonify({"message": "Error deleting user reviews", "error": str(e)}), 500
        
        # Delete user's cart items
        try:
            delete_cart_query = text("""
                DELETE FROM cart
                WHERE user_id = :user_id
            """)
            
            result = db.session.execute(
                delete_cart_query,
                {"user_id": user_id}
            )
            logger.debug(f"Deleted user's cart items")
        except Exception as e:
            logger.error(f"Error deleting cart items: {str(e)}")
            return jsonify({"message": "Error deleting user cart items", "error": str(e)}), 500
        
        # Delete user's order items and orders
        try:
            # First get all order IDs for this user
            order_ids_query = text("""
                SELECT id FROM orders
                WHERE user_id = :user_id
            """)
            
            order_ids_result = db.session.execute(
                order_ids_query,
                {"user_id": user_id}
            )
            
            order_ids = [row[0] for row in order_ids_result]
            
            # Delete order items for each order
            if order_ids:
                for order_id in order_ids:
                    delete_order_items_query = text("""
                        DELETE FROM order_items
                        WHERE order_id = :order_id
                    """)
                    
                    db.session.execute(
                        delete_order_items_query,
                        {"order_id": order_id}
                    )
                
                # Delete the orders
                delete_orders_query = text("""
                    DELETE FROM orders
                    WHERE user_id = :user_id
                """)
                
                db.session.execute(
                    delete_orders_query,
                    {"user_id": user_id}
                )
                
                logger.debug(f"Deleted user's orders and order items")
        except Exception as e:
            logger.error(f"Error deleting orders: {str(e)}")
            return jsonify({"message": "Error deleting user orders", "error": str(e)}), 500
        
        # Finally delete the user
        try:
            delete_user_query = text("""
                DELETE FROM users
                WHERE id = :user_id
            """)
            
            db.session.execute(
                delete_user_query,
                {"user_id": user_id}
            )
            logger.debug("User deleted successfully")
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return jsonify({"message": "Error deleting user record", "error": str(e)}), 500
        
        db.session.commit()
        logger.info(f"User {username} and all associated data deleted successfully")
        return jsonify({"message": f"User {username} deleted successfully"}), 200
            
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"SQLAlchemy error deleting user: {str(e)}")
        return jsonify({"message": "Database error while deleting user", "error": str(e)}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"General error deleting user: {str(e)}")
        return jsonify({"message": "Unexpected error while deleting user", "error": str(e)}), 500

@admin_bp.route("/admin/user/create", methods=["POST"])
@token_required
def create_user(current_user):
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({"message": "Unauthorized access"}), 403
    
    if not request.is_json:
        logger.error("Invalid JSON format in request")
        return jsonify({"message": "Invalid JSON format"}), 400
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ["username", "email", "full_name", "password"]
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"message": f"Missing required field: {field}"}), 400
    
    try:
        # Check if username is already taken
        username_check = db.session.execute(
            text("SELECT id FROM users WHERE username = :username"),
            {"username": data["username"]}
        ).fetchone()
        
        if username_check:
            return jsonify({"message": "Username already taken"}), 400
        
        # Check if email is already taken
        email_check = db.session.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": data["email"]}
        ).fetchone()
        
        if email_check:
            return jsonify({"message": "Email already taken"}), 400
        
        # Hash the password
        password_hash = generate_password_hash(data["password"])
        
        # Create new user
        insert_query = text("""
            INSERT INTO users (username, email, pass_word, full_name, user_address, phone_number, user_role)
            VALUES (:username, :email, :password, :full_name, :user_address, :phone_number, :user_role)
            RETURNING id
        """)
        
        result = db.session.execute(
            insert_query,
            {
                "username": data["username"],
                "email": data["email"],
                "password": password_hash,
                "full_name": data["full_name"],
                "user_address": data.get("user_address", ""),
                "phone_number": data.get("phone_number", ""),
                "user_role": data.get("user_role", "Customer")
            }
        )
        
        new_user_id = result.scalar()
        
        db.session.commit()
        logger.info(f"User {data['username']} created successfully with ID {new_user_id}")
        
        return jsonify({
            "message": "User created successfully",
            "user_id": new_user_id
        }), 201
            
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"SQLAlchemy error creating user: {str(e)}")
        return jsonify({"message": "Error creating user", "error": str(e)}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"General error creating user: {str(e)}")
        return jsonify({"message": "Error creating user", "error": str(e)}), 500
