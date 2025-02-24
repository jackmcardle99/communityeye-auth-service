import logging
import bcrypt
import jwt
import datetime
from flask import request, jsonify, make_response, Blueprint
from db import db_connect
from decorators import auth_required
from validations import validate_fields, valid_password, valid_email
import config
from typing import Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/api/v1/register", methods=["POST"])
def register() -> Tuple[make_response, int]:
    """
    Register a new user.

    This route handles user registration by validating input fields, hashing the password,
    and storing the user data in the database. It returns a JWT token upon successful registration.

    Returns:
        Tuple[make_response, int]: A Flask response object containing the JWT token or error message,
                                   along with the appropriate HTTP status code.
    """
    log_data = request.json.copy()
    if "password" in log_data:
        log_data["password"] = "**********"
    logger.info("Registration attempt with data: %s", log_data)

    if request.headers.get("x-access-token", None) is not None:
        logger.warning("Registration denied due to existing token.")
        return make_response(
            jsonify({"Forbidden": "Can't register with an existing token"}),
            401,
        )

    required_fields = [
        "first_name",
        "last_name",
        "email_address",
        "mobile_number",
        "city",
        "password",
    ]
    missing_fields = validate_fields(required_fields, request)
    if missing_fields:
        logger.warning(
            "Missing fields in registration data: %s", missing_fields
        )
        return make_response(
            jsonify(
                {
                    "Unprocessable entity": "Missing fields in JSON data",
                    "missing_fields": missing_fields,
                }
            ),
            422,
        )

    if not valid_password(request.json["password"]):
        logger.warning("Invalid password format.")
        return make_response(
            jsonify(
                {
                    "Unprocessable entity": "Invalid password. Password should be 8 to 16 characters and contain at least one numerical and non alpha-numerical character"
                }
            ),
            422,
        )

    if not valid_email(request.json["email_address"]):
        logger.warning("Invalid email address format.")
        return make_response(
            jsonify({"Unprocessable entity": "Invalid email address."}), 422
        )

    hashed_password = bcrypt.hashpw(
        request.json["password"].encode("utf-8"), bcrypt.gensalt()
    )
    logger.debug(
        "Generated hashed password: %s", hashed_password.decode("utf-8")
    )

    new_user = {
        "first_name": request.json["first_name"],
        "last_name": request.json["last_name"],
        "email_address": request.json["email_address"],
        "mobile_number": request.json["mobile_number"],
        "city": request.json["city"],
        "password": hashed_password.decode("utf-8"),
        "admin": False,
        "creation_time": datetime.datetime.now(),
    }

    try:
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (first_name, last_name, email_address, mobile_number, city, password, admin, creation_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING user_id;
        """,
            (
                new_user["first_name"],
                new_user["last_name"],
                new_user["email_address"],
                new_user["mobile_number"],
                new_user["city"],
                new_user["password"],
                new_user["admin"],
                new_user["creation_time"],
            ),
        )

        conn.commit()
        new_user_id = cursor.fetchone()[0]
        token = jwt.encode(
            {
                "user_id": str(new_user_id),
                "admin": new_user["admin"],
                "email_address": new_user["email_address"],
                "exp": datetime.datetime.utcnow()
                + datetime.timedelta(minutes=30),
            },
            config.secret_key,
            algorithm="HS256",
        )

        logger.info("User registered successfully with ID: %s", new_user_id)
        return make_response(jsonify({"token": token}), 201)

    except Exception as e:
        logger.error("Error during registration: %s", str(e))
        conn.rollback()
        return make_response(jsonify({"error": "Internal server error"}), 500)
    finally:
        cursor.close()
        conn.close()


@auth_bp.route("/api/v1/login", methods=["POST"])
def login() -> Tuple[make_response, int]:
    """
    Log in an existing user.

    This route handles user login by validating the email and password, and returning a JWT token
    upon successful authentication.

    Returns:
        Tuple[make_response, int]: A Flask response object containing the JWT token or error message,
                                   along with the appropriate HTTP status code.
    """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    logger.info("Login attempt with email: %s", email)

    if email and password:
        if not valid_email(email):
            logger.warning("Invalid email address format during login.")
            return make_response(
                jsonify({"Bad request": "Invalid email address"}), 400
            )

        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, admin, password FROM users WHERE email_address = %s",
                (email,),
            )
            user = cursor.fetchone()

            if user:
                user_id = user[0]
                admin = user[1]
                hashed_password = user[2]

                logger.debug(
                    "Retrieved hashed password from DB: %s", hashed_password
                )

                hashed_password_bytes = hashed_password.encode("utf-8")

                if bcrypt.checkpw(
                    password.encode("utf-8"), hashed_password_bytes
                ):
                    token = jwt.encode(
                        {
                            "user_id": user_id,
                            "admin": admin,
                            "email_address": email,
                            "exp": datetime.datetime.now(datetime.timezone.utc)
                            + datetime.timedelta(minutes=30),
                        },
                        config.secret_key,
                        algorithm="HS256",
                    )

                    logger.info(
                        "User logged in successfully with ID: %s", user_id
                    )
                    response_data = {"token": token}
                    return make_response(jsonify(response_data), 200)
                else:
                    logger.warning(
                        "Password is incorrect for email: %s", email
                    )
                    return make_response(
                        jsonify({"Forbidden": "Password is incorrect"}), 401
                    )
            else:
                logger.warning("Email address is incorrect: %s", email)
                return make_response(
                    jsonify({"Forbidden": "Email address is incorrect"}), 401
                )
        except Exception as e:
            logger.error("Error during login: %s", str(e))
            return make_response(
                jsonify({"error": "Internal server error"}), 500
            )
        finally:
            cursor.close()
            conn.close()

    logger.warning("Could not verify login attempt.")
    return make_response(
        "Could not verify",
        401,
        {"WWW-Authenticate": 'Basic realm="Login required"'},
    )


@auth_bp.route("/api/v1/logout", methods=["GET"])
@auth_required
def logout() -> Tuple[make_response, int]:
    """
    Log out a user by blacklisting the JWT token.

    This route handles user logout by adding the JWT token to a blacklist in the database.

    Returns:
        Tuple[make_response, int]: A Flask response object containing a success message or error message,
                                   along with the appropriate HTTP status code.
    """
    token = request.headers.get("x-access-token")
    if not token:
        logger.warning("Logout attempt failed: Token is missing.")
        return make_response(
            jsonify({"Bad request": "Token is missing."}), 400
        )

    try:
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO blacklisted_tokens (token, blacklisted_at) VALUES (%s, %s)",
            (token, datetime.datetime.now()),
        )
        conn.commit()
        logger.info(f"Token blacklisted successfully: {token}")
        return make_response(jsonify({"Success": "Logged out."}), 200)
    except Exception as e:
        logger.error(f"Error blacklisting token: {str(e)}")
        conn.rollback()
        return make_response(
            jsonify({"error": "Internal server error. Error logging out."}),
            500,
        )
    finally:
        cursor.close()
        conn.close()


@auth_bp.route("/api/v1/delete_account", methods=["DELETE"])
@auth_required
def delete_account() -> Tuple[make_response, int]:
    """
    Delete a user account.

    This route handles account deletion by removing the user from the database and blacklisting
    the JWT token.

    Returns:
        Tuple[make_response, int]: A Flask response object containing a success message or error message,
                                   along with the appropriate HTTP status code.
    """
    token = request.headers.get("x-access-token")

    try:
        decoded_token = jwt.decode(
            token, config.secret_key, algorithms=["HS256"]
        )
        user_id = decoded_token.get("user_id")

        if not user_id:
            logger.warning("Invalid token: No user_id found.")
            return make_response(jsonify({"Forbidden": "Invalid token."}), 401)

        conn = db_connect()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT user_id FROM users WHERE user_id = %s", (user_id,)
        )
        user = cursor.fetchone()

        if not user:
            logger.warning("Account deletion attempt failed: User not found.")
            return make_response(
                jsonify({"Not found": "User not found."}), 404
            )

        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        conn.commit()

        cursor.execute(
            "INSERT INTO blacklisted_tokens (token, blacklisted_at) VALUES (%s, %s)",
            (token, datetime.datetime.now()),
        )
        conn.commit()

        logger.info(
            f"Account with user ID {user_id} has been deleted successfully."
        )
        return make_response(
            jsonify({"Created": "Account deleted successfully."}), 201
        )

    except Exception as e:
        logger.error(f"Error during account deletion: {str(e)}")
        return make_response(
            jsonify(
                {"error": "Internal server error. Error deleting account."}
            ),
            500,
        )

    finally:
        cursor.close()
        conn.close()
