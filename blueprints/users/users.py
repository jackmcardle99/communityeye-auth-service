import logging
from flask import request, jsonify, make_response, Blueprint
from db import db_connect
from decorators import auth_required

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

users_bp = Blueprint('users_bp', __name__)

@users_bp.route("/api/v1/users/<int:user_id>", methods=["GET"])
@auth_required
def get_user(user_id):
    logger.info("Fetching data for user ID: %s", user_id)
    try:
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, first_name, last_name, email_address, mobile_number, city, admin, creation_time FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        if user:
            user_data = {
                'user_id': user[0],
                'first_name': user[1],
                'last_name': user[2],
                'email_address': user[3],
                'mobile_number': user[4],
                'city': user[5],
                'admin': user[6],
                'creation_time': user[7].isoformat()
            }
            logger.info("User data retrieved successfully: %s", user_data)
            return make_response(jsonify(user_data), 200)
        else:
            logger.warning("User not found with ID: %s", user_id)
            return make_response(jsonify({'error': 'User not found'}), 404)
    
    except Exception as e:
        logger.error("Error fetching user data: %s", str(e))
        return make_response(jsonify({'error': 'Internal server error'}), 500)
    
    finally:
        cursor.close()
        conn.close()
