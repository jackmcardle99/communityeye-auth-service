# import pytest
# from flask import Flask
# from unittest.mock import patch, MagicMock
# import sys
# import os

# # Add the project root to PYTHONPATH
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from blueprints.auth.auth import auth_bp
# import jwt
# import datetime

# # Create a test client for the Flask app
# @pytest.fixture
# def client():
#     app = Flask(__name__)
#     app.register_blueprint(auth_bp)
#     app.config['TESTING'] = True

#     with app.test_client() as client:
#         yield client

# # Mock the db_connect function
# @patch('db.db_connect')
# def test_register(mock_db_connect, client):
#     # Mock the database connection and cursor
#     mock_conn = MagicMock()
#     mock_cursor = MagicMock()
#     mock_db_connect.return_value = mock_conn
#     mock_conn.cursor.return_value = mock_cursor

#     # Mock the execute and fetchone methods
#     mock_cursor.execute.return_value = None
#     mock_cursor.fetchone.return_value = (1,)

#     # Mock the bcrypt and jwt functions
#     with patch('blueprints.auth.auth.bcrypt.hashpw', return_value=b'hashed_password'):
#         with patch('blueprints.auth.auth.jwt.encode', return_value='mocked_token'):
#             response = client.post('/api/v1/register', json={
#                 "first_name": "John",
#                 "last_name": "Doe",
#                 "email_address": "john.doe@example.com",
#                 "mobile_number": "1234567890",
#                 "city": "Sample City",
#                 "password": "Password123!"
#             })

#     assert response.status_code == 201
#     assert response.json['token'] == 'mocked_token'

# # Similar adjustments for other test functions...

# @patch('db.db_connect')
# def test_login(mock_db_connect, client):
#     # Mock the database connection and cursor
#     mock_conn = MagicMock()
#     mock_cursor = MagicMock()
#     mock_db_connect.return_value = mock_conn
#     mock_conn.cursor.return_value = mock_cursor

#     # Mock the execute and fetchone methods
#     mock_cursor.execute.return_value = None
#     mock_cursor.fetchone.return_value = (1, False, 'hashed_password')

#     # Mock the bcrypt and jwt functions
#     with patch('blueprints.auth.auth.bcrypt.checkpw', return_value=True):
#         with patch('blueprints.auth.auth.jwt.encode', return_value='mocked_token'):
#             response = client.post('/api/v1/login', json={
#                 "email": "john.doe@example.com",
#                 "password": "Password123!"
#             })

#     assert response.status_code == 200
#     assert response.json['token'] == 'mocked_token'

# @patch('db.db_connect')
# def test_logout(mock_db_connect, client):
#     # Mock the database connection and cursor
#     mock_conn = MagicMock()
#     mock_cursor = MagicMock()
#     mock_db_connect.return_value = mock_conn
#     mock_conn.cursor.return_value = mock_cursor

#     # Mock the execute method
#     mock_cursor.execute.return_value = None

#     # Mock the jwt decode function
#     with patch('blueprints.auth.auth.jwt.decode', return_value={'user_id': 1}):
#         response = client.get('/api/v1/logout', headers={
#             'x-access-token': 'mocked_token'
#         })

#     assert response.status_code == 200
#     assert response.json['Success'] == 'Logged out.'

# @patch('db.db_connect')
# def test_delete_account(mock_db_connect, client):
#     # Mock the database connection and cursor
#     mock_conn = MagicMock()
#     mock_cursor = MagicMock()
#     mock_db_connect.return_value = mock_conn
#     mock_conn.cursor.return_value = mock_cursor

#     # Mock the execute and fetchone methods
#     mock_cursor.execute.return_value = None
#     mock_cursor.fetchone.return_value = (1,)

#     # Mock the jwt decode function
#     with patch('blueprints.auth.auth.jwt.decode', return_value={'user_id': 1}):
#         response = client.delete('/api/v1/delete_account', headers={
#             'x-access-token': 'mocked_token'
#         })

#     assert response.status_code == 201
#     assert response.json['Created'] == 'Account deleted successfully.'

# @patch('db.db_connect')
# def test_validate_token(mock_db_connect, client):
#     # Mock the database connection and cursor
#     mock_conn = MagicMock()
#     mock_cursor = MagicMock()
#     mock_db_connect.return_value = mock_conn
#     mock_conn.cursor.return_value = mock_cursor

#     # Mock the execute and fetchone methods
#     mock_cursor.execute.return_value = None
#     mock_cursor.fetchone.return_value = None

#     response = client.post('/api/v1/validate-token', json={
#         'token': 'mocked_token'
#     })

#     assert response.status_code == 200
#     assert response.json['valid'] == True
import pytest
import bcrypt
import jwt
import datetime
from unittest.mock import patch, MagicMock
from flask import Flask, json
from blueprints.auth.auth import auth_bp
import config

# Create a test client for the Flask app
@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(auth_bp)
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client

def test_register_success(client):
    user_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email_address": "johndoe@example.com",
        "mobile_number": "1234567890",
        "city": "Test City",        
        "password": "Test@1234",        
    }
    # hashed_password = bcrypt.hashpw(user_data["password"].encode("utf-8"), bcrypt.gensalt())
    # user_data["password"] = hashed_password.decode("utf-8")
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = [1]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("db.db_connect", return_value=mock_conn):
        response = client.post("/api/v1/register", data=json.dumps(user_data), content_type="application/json")
        assert response.status_code == 201
        assert "token" in response.json

def test_register_missing_fields(client):
    response = client.post("/api/v1/register", data=json.dumps({}), content_type="application/json")
    assert response.status_code == 422
    assert "missing_fields" in response.json

def test_login_success(client):
    email = "johndoe@example.com"
    password = "Test@1234"
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = [1, False, hashed_password]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("db.db_connect", return_value=mock_conn):
        response = client.post("/api/v1/login", data=json.dumps({"email": email, "password": password}), content_type="application/json")
        assert response.status_code == 200
        assert "token" in response.json

def test_login_invalid_password(client):
    email = "johndoe@example.com"
    password = "WrongPass123"
    hashed_password = bcrypt.hashpw("Test@1234".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = [1, False, hashed_password]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("db.db_connect", return_value=mock_conn):
        response = client.post("/api/v1/login", data=json.dumps({"email": email, "password": password}), content_type="application/json")
        assert response.status_code == 401
        assert "Forbidden" in response.json

def test_logout_success(client):
    token = jwt.encode({"user_id": "1", "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, config.FLASK_SECRET_KEY, algorithm="HS256")
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("db.db_connect", return_value=mock_conn):
        response = client.get("/api/v1/logout", headers={"x-access-token": token})
        assert response.status_code == 200
        assert "Success" in response.json

def test_delete_account_success(client):
    token = jwt.encode({"user_id": "1", "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, config.FLASK_SECRET_KEY, algorithm="HS256")
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = [1]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("db.db_connect", return_value=mock_conn):
        response = client.delete("/api/v1/delete_account", headers={"x-access-token": token})
        assert response.status_code == 201
        assert "Created" in response.json

def test_validate_token_success(client):
    token = jwt.encode({"user_id": "1", "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, config.FLASK_SECRET_KEY, algorithm="HS256")
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None  # Token is not blacklisted
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("db.db_connect", return_value=mock_conn):
        response = client.post("/api/v1/validate-token", data=json.dumps({"token": token}), content_type="application/json")
        assert response.status_code == 200
        assert response.json["valid"] is True

def test_validate_token_blacklisted(client):
    token = jwt.encode(
    {"user_id": "1", "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=30)},
    config.FLASK_SECRET_KEY,
    algorithm="HS256"
    )

    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = [1]  # Token is blacklisted
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    with patch("db.db_connect", return_value=mock_conn):
        response = client.post("/api/v1/validate-token", data=json.dumps({"token": token}), content_type="application/json")
        assert response.status_code == 401
        assert response.json["valid"] is False
