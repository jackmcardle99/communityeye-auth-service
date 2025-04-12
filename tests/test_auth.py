"""
File: test_auth.py
Author: Jack McArdle

This file is part of CommunityEye.

Email: mcardle-j9@ulster.ac.uk
B-No: B00733578
"""

import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from blueprints.auth.auth import auth_bp
import jwt
import config

MOCK_TOKEN = jwt.encode({'user_id': 1, 'email_address': 'user@example.com', 'admin': False}, config.FLASK_SECRET_KEY, algorithm='HS256')

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(auth_bp)
        self.client = self.app.test_client()

    # /api/v1/register
    @patch('blueprints.auth.auth.db_connect')
    @patch('blueprints.auth.auth.valid_email', return_value=True)
    @patch('blueprints.auth.auth.valid_password', return_value=True)
    def test_register_success(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [None, [1]]
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        payload = {
            "first_name": "John",
            "last_name": "Doe",
            "email_address": "john@example.com",
            "mobile_number": "1234567890",
            "city": "Belfast",
            "password": "Password1!"
        }
        response = self.client.post('/api/v1/register', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.json)

    def test_register_with_token_header(self):
        response = self.client.post('/api/v1/register', headers={'x-access-token': MOCK_TOKEN})
        self.assertEqual(response.status_code, 401)

    def test_register_missing_fields(self):
        response = self.client.post('/api/v1/register', json={})
        self.assertEqual(response.status_code, 422)

    # /api/v1/login
    @patch('blueprints.auth.auth.db_connect')
    @patch('blueprints.auth.auth.valid_email', return_value=True)
    @patch('bcrypt.checkpw', return_value=True)
    def test_login_success(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1, False, '$2b$12$hashedpassword')
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        payload = {'email': 'john@example.com', 'password': 'Password1!'}
        response = self.client.post('/api/v1/login', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json)

    def test_login_invalid_email_format(self):
        payload = {'email': 'invalid-email', 'password': 'pass'}
        response = self.client.post('/api/v1/login', json=payload)
        self.assertEqual(response.status_code, 400)

    @patch('blueprints.auth.auth.db_connect')
    def test_login_wrong_password(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1, False, '$2b$12$hashedpassword')
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        with patch('bcrypt.checkpw', return_value=False):
            payload = {'email': 'john@example.com', 'password': 'WrongPass'}
            response = self.client.post('/api/v1/login', json=payload)
            self.assertEqual(response.status_code, 401)

    # /api/v1/logout
    @patch('blueprints.auth.auth.db_connect')
    def test_logout_success(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        response = self.client.get('/api/v1/logout', headers={'x-access-token': MOCK_TOKEN})
        self.assertEqual(response.status_code, 200)

    def test_logout_missing_token(self):
        response = self.client.get('/api/v1/logout')
        self.assertEqual(response.status_code, 400)

    @patch('blueprints.auth.auth.db_connect')
    def test_logout_db_error(self, mock_db):
        mock_conn = MagicMock()
        mock_conn.cursor.side_effect = Exception("DB error")
        mock_db.return_value = mock_conn

        response = self.client.get('/api/v1/logout', headers={'x-access-token': MOCK_TOKEN})
        self.assertEqual(response.status_code, 500)

    # /api/v1/delete_account
    @patch('blueprints.auth.auth.db_connect')
    def test_delete_account_success(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        response = self.client.delete('/api/v1/delete_account', headers={'x-access-token': MOCK_TOKEN})
        self.assertEqual(response.status_code, 204)

    def test_delete_account_invalid_token(self):
        invalid_token = jwt.encode({'foo': 'bar'}, config.FLASK_SECRET_KEY, algorithm='HS256')
        response = self.client.delete('/api/v1/delete_account', headers={'x-access-token': invalid_token})
        self.assertEqual(response.status_code, 401)

    @patch('blueprints.auth.auth.db_connect')
    def test_delete_account_user_not_found(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        response = self.client.delete('/api/v1/delete_account', headers={'x-access-token': MOCK_TOKEN})
        self.assertEqual(response.status_code, 404)

    # /api/v1/validate-token
    @patch('blueprints.auth.auth.db_connect')
    def test_validate_token_success(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None 
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        response = self.client.post('/api/v1/validate-token', json={'token': MOCK_TOKEN})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['valid'])

    @patch('blueprints.auth.auth.db_connect')
    def test_validate_token_blacklisted(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = True
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        response = self.client.post('/api/v1/validate-token', json={'token': MOCK_TOKEN})
        self.assertEqual(response.status_code, 401)

    def test_validate_token_missing(self):
        response = self.client.post('/api/v1/validate-token', json={})
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()
