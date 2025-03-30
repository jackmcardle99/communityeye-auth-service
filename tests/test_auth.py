import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from blueprints.auth.auth import auth_bp  # Adjust the import to reflect the directory structure
from werkzeug.security import generate_password_hash, check_password_hash

# Mocked data for the user
USER_EMAIL = 'john.doe@example.com'
USER_PASSWORD = 'P@ssword123'

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(auth_bp)
        self.client = self.app.test_client()

    @patch('blueprints.auth.auth.db_connect')
    def test_register_success(self, mock_db_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # Simulate no existing user

        # Mock the successful insert and return a fake user ID
        mock_cursor.fetchone.return_value = (1,)  # Simulate user ID return
        response = self.client.post('/api/v1/register', json={
            "first_name": "John",
            "last_name": "Doe",
            "email_address": "john.doe@example.com",
            "mobile_number": "1234567890",
            "city": "Sample City",
            "password": "Pass1@23"
        })
        self.assertEqual(response.status_code, 201)

    def test_register_missing_fields(self):
        response = self.client.post('/api/v1/register', json={
            "first_name": "John",
            "last_name": "Doe",
            "email_address": "john.doe@example.com",
        })
        self.assertEqual(response.status_code, 422)

    def test_register_with_token(self):
        response = self.client.post('/api/v1/register', headers={"x-access-token": "dummy_token"}, json={
            "first_name": "John",
            "last_name": "Doe",
            "email_address": "john.doe@example.com",
            "mobile_number": "1234567890",
            "city": "Sample City",
            "password": "SecureP@ss123"
        })
        self.assertEqual(response.status_code, 401)

    @patch('blueprints.auth.auth.db_connect')
    @patch('werkzeug.security.check_password_hash')
    def test_login_success(self, mock_check_password_hash, mock_db_connect):
        # Step 1: Register the user first
        registration_response = self.client.post('/api/v1/register', json={
            'email_address': USER_EMAIL,
            'first_name': 'John',
            'last_name': 'Doe',
            'mobile_number': '1234567890',
            'city': 'Sample City',
            'password': USER_PASSWORD
        })
        self.assertEqual(registration_response.status_code, 201)  # Ensure registration is successful
        registration_token = registration_response.json['token']  # Get the token from registration response

        # Step 2: Mock database connection and cursor for login
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        # mock_cursor.fetchone.return_value = (1, USER_EMAIL, generate_password_hash(USER_PASSWORD))

        # Mock password check to return True
        mock_check_password_hash.return_value = True

        # Step 3: Simulate the login request with the registration token
        login_response = self.client.post('/api/v1/login', json={
            'email_address': USER_EMAIL,
            'password': USER_PASSWORD
        })

        # Step 4: Assert login is successful
        self.assertEqual(login_response.status_code, 200)
        self.assertIn('token', login_response.json) 


    def test_login_invalid_credentials(self):
        response = self.client.post('/api/v1/login', json={
            "email": "john.doe@example.com",
            "password": "WrongPass123"
        })
        self.assertEqual(response.status_code, 401)

    @patch('blueprints.auth.auth.db_connect')
    @patch('blueprints.auth.auth.validate_token')
    def test_delete_account_success(self, mock_validate_token, mock_db_connect):
        # Step 1: Register the user first
        registration_response = self.client.post('/api/v1/register', json={
            'email_address': USER_EMAIL,
            'first_name': 'John',
            'last_name': 'Doe',
            'mobile_number': '1234567890',
            'city': 'Sample City',
            'password': USER_PASSWORD
        })
        self.assertEqual(registration_response.status_code, 201)  # Ensure registration is successful
        registration_token = registration_response.json['token']  # Get the token from registration response

        # Step 2: Mock the database connection and user retrieval for account deletion
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (1, 'john.doe@example.com', generate_password_hash('correct_password'))

        # Mock token validation to return a valid user payload
        mock_validate_token.return_value = {'user_id': 1}  # Simulate a valid token with a user ID

        # Step 3: Simulate the delete account request with the registration token
        delete_response = self.client.delete('/api/v1/delete_account', headers={'Authorization': registration_token})

        # Step 4: Assert the deletion was successful (204 No Content)
        self.assertEqual(delete_response.status_code, 204)

    @patch('blueprints.auth.auth.db_connect')
    def test_validate_token_success(self, mock_db_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # Simulate token not blacklisted

        response = self.client.post('/api/v1/validate-token', json={"token": "valid_token"})
        self.assertEqual(response.status_code, 200)

    def test_validate_token_missing(self):
        response = self.client.post('/api/v1/validate-token', json={})
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()