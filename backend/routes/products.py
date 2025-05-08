from flask import Blueprint, jsonify, request
from backend.extensions import db
import logging
from sqlalchemy.exc import SQLAlchemyError
from backend.routes.auth import token_required
from sqlalchemy import text
from decimal import Decimal


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
product_bp = Blueprint('product', __name__)


#############################################################################get_products#########################################################    

@product_bp.route('/products', methods=['GET'])
def get_products():
    try:
        # Fetch category_id of query parameters (optional)
        category_id = request.args.get('category_id', default=None, type=int)

        # Perform the stored procedure with category_id passed
        result = db.session.execute(
            "EXEC GetAllProducts @category_id = :category_id",
            {'category_id': category_id}
        )
        products = result.fetchall()

        # Check the status of "fail"
        if products and 'status' in products[0].keys() and products[0]['status'] == 'fail':
            logger.info(f"No products found for category_id {category_id if category_id else 'all'}: {products[0]['message']}")
            return jsonify({'message': products[0]['message'], 'status_code': products[0]['StatusCode']}), 200

        # Product menu configuration
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
        
        logger.info(f"Retrieved {len(formatted_products)} products for category_id {category_id if category_id else 'all'}")
        return jsonify({'products': formatted_products}), 200

    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error fetching products: {str(e)}")
        return jsonify({'message': 'Error fetching products', 'error': str(e)}), 500
    except Exception as e:
        logger.error(f"General error fetching products: {str(e)}")
        return jsonify({'message': 'Error flowing products', 'error': str(e)}), 500
#############################################################################get_product_details#########################################################    

@product_bp.route('/product/<string:product_name>', methods=['GET'])
@token_required
def get_product_details(current_user, product_name):
    try:
        # Pagination parameters
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)

        # Validation of pagination parameters
        if page < 1 or per_page < 1:
            logger.warning(f"Invalid pagination parameters for product {product_name}: page={page}, per_page={per_page}")
            return jsonify({
                'status': 'fail',
                'message': 'Invalid pagination parameters',
                'status_code': 4
            }), 400

        # Fetch Product Details
        logger.debug(f"Fetching product details for: {product_name}")
        product_result = db.session.execute(text("""
            EXEC GetProductDetails @ProductName = :product_name
        """), {'product_name': product_name})
        product_row = product_result.fetchone()

        # Close the result set
        product_result.close()

        # Check if product exists or if there's a failure status
        if not product_row:
            logger.warning(f"Product not found: {product_name}")
            return jsonify({
                'status': 'fail',
                'message': 'Product not found',
                'status_code': 2
            }), 404

        if 'status' in product_row.keys() and product_row['status'] == 'fail':
            logger.warning(f"Failed to fetch product details for {product_name}: {product_row['message']}")
            return jsonify({
                'status': 'fail',
                'message': product_row['message'],
                'status_code': product_row['StatusCode']
            }), 404

        # Format product details
        discounted_price = float(product_row['price']) * (1 - float(product_row['discount']) / 100)
        product_details = {
            'product_id': product_row['product_id'],
            'product_name': product_row['product_name'],
            'description': product_row['product_description'],
            'price': float(product_row['price']) if isinstance(product_row['price'], Decimal) else product_row['price'],
            'discounted_price': round(discounted_price, 2),
            'stock': product_row['stock'],
            'stock_status': 'In Stock' if product_row['stock'] > 0 else 'Out of Stock',
            'category_name': product_row['category_name'],
            'image_url': product_row['image_url'],
            'discount': float(product_row['discount']) if isinstance(product_row['discount'], Decimal) else product_row['discount']
        }

        # Fetch reviews
        logger.debug(f"Fetching reviews for product: {product_name}, page: {page}, per_page: {per_page}")
        reviews_result = db.session.execute(text("""
            EXEC GetReviewsForSpecificProduct 
                @ProductName = :product_name,
                @Page = :page,
                @PerPage = :per_page
        """), {'product_name': product_name, 'page': page, 'per_page': per_page})

        reviews = []
        reviews_status_row = None
        for row in reviews_result:
            if 'status' in row.keys():
                reviews_status_row = row
            else:
                reviews.append({
                    'product_id': row['product_id'],
                    'product_name': row['product_name'],
                    'user_id': row['user_id'],
                    'username': row['username'],
                    'rating': float(row['rating']) if isinstance(row['rating'], Decimal) else row['rating'],
                    'review_text': row['review_text'],
                    'review_date': str(row['review_date']),
                    'photo_url': row['photo_url']
                })
        reviews_result.close()

        if reviews_status_row and reviews_status_row['status'] == 'fail':
            logger.info(f"No reviews found for product {product_name}: {reviews_status_row['message']}")
            reviews = []

        # Fetch average rating and total reviews
        avg_rating_result = db.session.execute(text("""
            SELECT 
                AVG(CAST(rating AS FLOAT)) AS average_rating,
                COUNT(rating) AS total_reviews
            FROM product_reviews
            WHERE product_id = :product_id
        """), {'product_id': product_row['product_id']}).fetchone()

        product_details['average_rating'] = round(avg_rating_result['average_rating'], 1) if avg_rating_result['average_rating'] else 0
        product_details['total_reviews'] = avg_rating_result['total_reviews']

        # Check if the user can add a review
        existing_review = db.session.execute(
            "SELECT 1 FROM product_reviews WHERE product_id = :product_id AND user_id = :user_id",
            {'product_id': product_row['product_id'], 'user_id': current_user.id}
        ).fetchone()
        can_review = not existing_review

        # Pagination
        total_reviews = avg_rating_result['total_reviews']
        total_pages = (total_reviews + per_page - 1) // per_page if total_reviews > 0 else 1

        logger.info(f"Retrieved product details and {len(reviews)} reviews for product: {product_name}, page: {page}")
        return jsonify({
            'status': 'success',
            'message': 'Product details and reviews retrieved successfully.',
            'status_code': 0,
            'product': product_details,
            'reviews': reviews,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_reviews': total_reviews,
                'total_pages': total_pages
            },
            'can_review': can_review
        }), 200

    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error fetching product details for {product_name}: {str(e)}")
        return jsonify({'status': 'fail', 'message': f'Database error: {str(e)}'}), 500
    except Exception as e:
        logger.error(f"General error fetching product details for {product_name}: {str(e)}")
        return jsonify({'status': 'fail', 'message': f'Server error: {str(e)}'}), 500
#############################################################################add_product_review#########################################################    

@product_bp.route('/product/<string:product_name>/review', methods=['POST'])
@token_required
def add_product_review(current_user, product_name):

    try:
        # Fetch audit data from the request
        data = request.get_json()
        rating = data.get('rating')
        review_text = data.get('review_text', '')
        username = current_user.username  # Use the username of the token

        # Perform an action to add the review
        result = db.session.execute(
            "EXEC AddProductReview @ProductName=:product_name, @Username=:username, @Rating=:rating, @ReviewText=:review_text",
            {
                'product_name': product_name,
                'username': username,
                'rating': rating,
                'review_text': review_text
            }
        )
        row = result.fetchone()

        if row and row['status'] == 'fail':
            logger.warning(f"Failed to add review for product {product_name}: {row['message']}")
            return jsonify({'status': row['status'], 'message': row['message'], 'status_code': row['StatusCode']}), 400

        # If successful, return audit details
        if row and row['status'] == 'success':
            db.session.commit()
            logger.info(f"Review added by user {current_user.id} for product {product_name}")
            return jsonify({
                'status': row['status'],
                'message': row['message'],
                'status_code': row['StatusCode'],
                'review': {
                    'review_id': row['review_id'],
                    'product_id': row['product_id'],
                    'user_id': row['user_id'],
                    'rating': row['rating'],
                    'review_text': row['review_text'],
                    'review_date': str(row['review_date'])
                }
            }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"SQLAlchemy error adding review for product {product_name}: {str(e)}")
        return jsonify({'status': 'fail', 'message': f'Database error: {str(e)}'}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"General error adding review for product {product_name}: {str(e)}")
        return jsonify({'status': 'fail', 'message': f'Server error: {str(e)}'}), 500
    
#############################################################################delete_review#########################################################    
@product_bp.route('/product/<string:product_name>/review', methods=['DELETE'])
@token_required
def delete_review(current_user, product_name):

    try:

        result = db.session.execute(
            "EXEC DeleteProductReview @ProductName=:product_name, @Username=:username",
            {
                "product_name": product_name,
                "username": current_user.username 
            }
        )
        row = result.fetchone()
        if row and row[0] == 'success':
            db.session.commit()
            logger.info(f"Review deleted for product {product_name} by user {current_user.username }")
            return jsonify({'message': row[2]}), 200
        else:
            db.session.rollback()
            logger.warning(f"Failed to delete review for product {product_name} by user {current_user.username }: {row[2] if row else 'No response'}")
            return jsonify({'message': row[2] if row else 'Error deleting review'}), 400

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"SQLAlchemy error deleting review: {str(e)}")
        return jsonify({'message': 'Error deleting review', 'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"General error deleting review: {str(e)}")
        return jsonify({'message': 'Error deleting review', 'error': str(e)}), 500
    

# mahmoud