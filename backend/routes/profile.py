from flask import Blueprint, jsonify, request
from backend.extensions import db
from backend.models.User import User
from backend.routes.auth import token_required  # Ensure correct import
import logging
from werkzeug.security import generate_password_hash, check_password_hash

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

profile_bp = Blueprint("profile", __name__)

@profile_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    try:
        user_data = {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'full_name': current_user.full_name,
            'user_address': current_user.user_address,
            'phone_number': current_user.phone_number,
            'user_role': current_user.user_role
        }
        
        return jsonify({
            'success': True,
            'message': 'Profile retrieved successfully',
            'user': user_data
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving profile: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error retrieving profile: {str(e)}'
        }), 500

@profile_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    try:
        data = request.get_json()
        
        # Update user fields
        if 'full_name' in data:
            current_user.full_name = data['full_name']
        if 'user_address' in data:
            current_user.user_address = data['user_address']
        if 'phone_number' in data:
            current_user.phone_number = data['phone_number']
        if 'email' in data:
            current_user.email = data['email']
            
        # Update password if provided
        if 'current_password' in data and 'new_password' in data:
            if not check_password_hash(current_user.pass_word, data['current_password']):
                return jsonify({
                    'success': False,
                    'message': 'Current password is incorrect'
                }), 400
                
            current_user.pass_word = generate_password_hash(data['new_password'])
            
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating profile: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error updating profile: {str(e)}'
        }), 500
