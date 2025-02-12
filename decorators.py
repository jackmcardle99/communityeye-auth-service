from functools import wraps
from flask import request, jsonify, make_response, g
import jwt
from db import db_connect
import logging
from globals import secret_key

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def auth_required(func):
    @wraps(func)
    def auth_required_wrapper(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            logger.warning("Unauthorized access attempt: Token is missing.")
            return make_response(jsonify({'Unauthorized': 'Token is missing.'}), 401)

        try:
            data = jwt.decode(token, secret_key, algorithms=['HS256'])
            # set global variables for resource validation
            g.user_id = data.get('user_id')
            g.admin = data.get('admin')
        except jwt.InvalidTokenError as e:
            logger.warning(f"Unauthorized access attempt: Invalid token. Error: {str(e)}")
            return make_response(jsonify({'Unauthorized': 'Token is invalid.'}), 401)

        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM blacklisted_tokens WHERE token = %s", (token,))
            bl_token = cursor.fetchone()
            if bl_token:
                logger.warning(f"Unauthorized access attempt: Token has been cancelled. Token: {token}")
                return make_response(jsonify({'Unauthorized': 'Token has been cancelled.'}), 401)
        except Exception as e:
            logger.error(f"Error checking token blacklist: {str(e)}")
            return make_response(jsonify({'Unauthorized': 'Error checking token blacklist.'}), 500)
        finally:
            cursor.close()
            conn.close()

        logger.info(f"Authorized access for user ID: {g.user_id}")
        return func(*args, **kwargs)

    return auth_required_wrapper
