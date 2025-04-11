import logging
import bcrypt
from flask import jsonify, make_response, Blueprint, request
from db import db_connect
from decorators import auth_required
from typing import Tuple

from validations import valid_email, valid_password

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


@users_bp.route("/api/v1/users/<int:user_id>", methods=["PUT"])
@auth_required
def update_user(user_id: int) -> make_response:
    """
    Update user data for a given user ID.

    This route handler updates user information in the database based on the provided user ID.
    It expects a JSON payload with the fields to be updated and returns a success message or an error message.

    Args:
        user_id (int): The ID of the user to update data for.

    Returns:
        Tuple[make_response, int]: A Flask response object containing the success or error message,
                                   along with the appropriate HTTP status code.
    """
    logger.info("Updating data for user ID: %s", user_id)
    data = request.get_json()

    if not data:
        logger.warning("No data provided for update for user ID: %s", user_id)
        return make_response(jsonify({"error": "No data provided"}), 400)

    fields_to_update = ["first_name", "last_name", "email_address", "mobile_number", "city", "password"]
    update_query = "UPDATE users SET "
    update_values = []

    for field in fields_to_update:
        if field in data:
            if field == "password":
                if not valid_password(data[field]):
                    logger.warning("Invalid password format for user ID: %s", user_id)
                    return make_response(jsonify({"error": "Invalid password format"}), 422)
                hashed_password = bcrypt.hashpw(data[field].encode("utf-8"), bcrypt.gensalt())
                update_query += f"{field} = %s, "
                update_values.append(hashed_password.decode("utf-8"))
            if field == "email_address":
                if not valid_email(data[field]):
                    logger.warning("Invalid email format for user ID: %s", user_id)
                    return make_response(jsonify({"error": "Invalid email format"}), 422)
            else:
                update_query += f"{field} = %s, "
                update_values.append(data[field])

    if not update_values:
        logger.warning("No valid fields provided for update for user ID: %s", user_id)
        return make_response(jsonify({"error": "No valid fields provided"}), 400)

    update_query = update_query.rstrip(", ")
    update_query += " WHERE user_id = %s"
    update_values.append(user_id)

    try:
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute(update_query, update_values)
        conn.commit()

        if cursor.rowcount == 0:
            logger.warning("User not found with ID: %s", user_id)
            return make_response(jsonify({"Not found": "User not found"}), 404)

        logger.info("User data updated successfully for user ID: %s", user_id)
        return make_response(jsonify({"success": "User data updated successfully"}), 200)

    except Exception as e:
        logger.error("Error updating user data: %s", str(e))
        return make_response(jsonify({"error": "Internal server error"}), 500)

    finally:
        cursor.close()
        conn.close()