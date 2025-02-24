import logging
from flask import jsonify, make_response, Blueprint
from db import db_connect
from decorators import auth_required
from typing import Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

users_bp = Blueprint("users_bp", __name__)


@users_bp.route("/api/v1/users/<int:user_id>", methods=["GET"])
@auth_required
def get_user(user_id: int) -> make_response:
    """
    Fetch and return user data for a given user ID.

    This route handler retrieves user information from the database based on the provided user ID.
    It returns the user data as a JSON response if the user is found, or an error message if not.

    Args:
        user_id (int): The ID of the user to fetch data for.

    Returns:
        Tuple[make_response, int]: A Flask response object containing the user data or error message,
                                   along with the appropriate HTTP status code.
    """
    logger.info("Fetching data for user ID: %s", user_id)
    try:
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, first_name, last_name, email_address, mobile_number, city, admin, creation_time FROM users WHERE user_id = %s",
            (user_id,),
        )
        user = cursor.fetchone()

        if user:
            user_data = {
                "user_id": user[0],
                "first_name": user[1],
                "last_name": user[2],
                "email_address": user[3],
                "mobile_number": user[4],
                "city": user[5],
                "admin": user[6],
                "creation_time": user[7].isoformat(),
            }
            logger.info("User data retrieved successfully: %s", user_data)
            return make_response(jsonify(user_data), 200)
        else:
            logger.warning("User not found with ID: %s", user_id)
            return make_response(jsonify({"Not found": "User not found"}), 404)

    except Exception as e:
        logger.error("Error fetching user data: %s", str(e))
        return make_response(jsonify({"error": "Internal server error"}), 500)

    finally:
        cursor.close()
        conn.close()
