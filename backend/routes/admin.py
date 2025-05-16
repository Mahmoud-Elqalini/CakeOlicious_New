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
        
        
        try:
            product_count_result = db.session.execute(text("SELECT COUNT(*) FROM products")).scalar()
            product_count = int(product_count_result) if product_count_result is not None else 0
            response_data["stats"]["totalProducts"] = product_count
            logger.info(f"Product count: {product_count}")
        except Exception as e:
            logger.error(f"Error getting product count: {str(e)}")
        
        
        try:
            user_count_result = db.session.execute(text("SELECT COUNT(*) FROM users")).scalar()
            user_count = int(user_count_result) if user_count_result is not None else 0
            response_data["stats"]["totalUsers"] = user_count
            logger.info(f"User count: {user_count}")
        except Exception as e:
            logger.error(f"Error getting user count: {str(e)}")
        
        
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
        
        
        try:
            recent_orders_query = text("""
                SELECT o.id, o.total_price, o.created_at, u.username 
                FROM orders o
                JOIN users u ON o.user_id = u.id
                ORDER BY o.created_at DESC
                LIMIT 5""")
            
            recent_orders = db.session.execute(recent_orders_query).fetchall()
            
            
        except Exception as e:
            logger.error(f"Error fetching recent orders: {str(e)}")
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error in admin dashboard: {str(e)}")
        return jsonify({"message": "Error fetching admin dashboard data", "error": str(e)}), 500

@admin_bp.route("/admin/products", methods=["GET"])
@token_required
def get_admin_products(current_user):
    if not check_admin(current_user):
        logger.warning(f"Unauthorized access attempt for user_id: {current_user.id}")
        return jsonify({"message": "Unauthorized access"}), 403
    
    try:
        
        products_query = text("""
            SELECT p.*, c.category_name 
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            ORDER BY p.id DESC """)
        
        products_result = db.session.execute(products_query).fetchall()
        
        products = []
        for row in products_result:
            product = {
                "id": row.id,
                "product_name": row.product_name,
                "description": row.product_description,
                "price": float(row.price),
                "stock": row.stock,
                "category_id": row.category_id,
                "category_name": row.category_name,
                "image_url": row.image_url,
                "is_active": bool(row.is_active) if hasattr(row, 'is_active') else True,
                "discount": float(row.discount) if hasattr(row, 'discount') else 0.0
            }
            products.append(product)
        
        return jsonify({"success": True, "products": products}), 200
        
    except Exception as e:
        logger.error(f"Error fetching products: {str(e)}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500


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
