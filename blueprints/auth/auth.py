import psycopg2
from psycopg2 import sql
import bcrypt
import jwt
import datetime
from flask import request, jsonify, make_response, Blueprint
from db import db_connect
from validations import validate_fields, valid_password, valid_email
import globals
# from werkzeug.security import generate_password_hash


auth_bp = Blueprint('auth_bp', __name__)
# reports = globals.db.reports

# Assuming you're using psycopg2 to connect to PostgreSQL
# Replace this with your actual database connection setup


@auth_bp.route("/api/v1/register", methods=["POST"])
def register():
    # Don't want to allow registration if someone is logged in
    if request.headers.get('x-access-token', None) is not None:
        return make_response(jsonify({"Forbidden": "Can't register with an existing token."}), 401)

    required_fields = ['first_name', 'last_name', 'email_address', 'mobile_number', 'city', 'password']
    missing_fields = validate_fields(required_fields, request)
    if missing_fields:
        return make_response(
            jsonify({'Unprocessable Entity': 'Missing fields in form data.', 'missing_fields': missing_fields}), 422)

    if not valid_password(request.form['password']):
        return make_response(
            jsonify({'Unprocessable Entity': 'Invalid password. Password should be 8 or more characters.'}), 422)

    # Hash the password using bcrypt
    hashed_password = bcrypt.hashpw(request.form['password'].encode("utf-8"), bcrypt.gensalt())

    # Debug: print the hashed password
    print(f"Generated hashed password: {hashed_password.decode('utf-8')}")  # Debugging line

    # Prepare the user data
    new_user = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email_address': request.form['email_address'],
        'mobile_number': request.form['mobile_number'],
        'city': request.form['city'],
        'password': hashed_password.decode('utf-8'),
        'admin': False, 
        'creation_time': datetime.datetime.now()
    }

    # Insert user data into PostgreSQL
    try:
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (first_name, last_name, email_address, mobile_number, city, password, admin, creation_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING user_id;
        """, (
            new_user['first_name'],
            new_user['last_name'],
            new_user['email_address'],
            new_user['mobile_number'],
            new_user['city'],
            new_user['password'],
            new_user['admin'],
            new_user['creation_time'],
        ))

        # Commit the transaction
        conn.commit()

        # Fetch the newly inserted user ID
        new_user_id = cursor.fetchone()[0]

        # Generate JWT token
        token = jwt.encode({
            'user_id': str(new_user_id),
            'admin': new_user['admin'],
            'email_address': new_user['email_address'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
            globals.secret_key,
            algorithm='HS256'
        )

        return make_response(jsonify({'token': token}), 201)

    except Exception as e:
        conn.rollback()
        return make_response(jsonify({'error': str(e)}), 500)
    finally:
        cursor.close()
        conn.close()



@auth_bp.route("/api/v1/login", methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if email and password:
        try:
            conn = db_connect()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, admin, password FROM users WHERE email_address = %s", (email,))
            user = cursor.fetchone()

            if user:
                user_id = user[0]
                admin = user[1]
                hashed_password = user[2]

                # Debugging line to check the retrieved hashed password
                print(f"Retrieved hashed password from DB: {hashed_password}")  # Debugging line

                # Ensure hashed_password is in bytes
                hashed_password_bytes = hashed_password.encode('utf-8')

                # Check password
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password_bytes):
                    # Encode essential user data in the token
                    token = jwt.encode({
                        'id': user_id,
                        'admin': admin,
                        'email_address': email,
                        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
                    }, globals.secret_key, algorithm='HS256')

                    # Prepare the response with the token
                    response_data = {
                        'token': token
                    }
                    return make_response(jsonify(response_data), 200)
                else:
                    return make_response(jsonify({'error': 'Password is incorrect.'}), 401)
            else:
                return make_response(jsonify({'error': 'Email address is incorrect.'}), 401)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 500)
        finally:
            cursor.close()
            conn.close()

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required"'})
