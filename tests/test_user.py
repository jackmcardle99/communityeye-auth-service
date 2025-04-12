"""
File: test_user.py
Author: Jack McArdle

This file is part of CommunityEye.

Email: mcardle-j9@ulster.ac.uk
B-No: B00733578
"""

import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from blueprints.users.users import users_bp
import jwt
import config

MOCK_TOKEN = jwt.encode({'user_id': 1, 'email_address': 'user@example.com', 'admin': False}, config.FLASK_SECRET_KEY, algorithm='HS256')

class UserTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(users_bp)
        self.client = self.app.test_client()

    # GET /api/v1/users/<user_id>
    @patch('blueprints.users.users.db_connect')
    def test_get_user_success(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1, 'John', 'Doe', 'john@example.com', '1234567890', 'Belfast', False, MagicMock(isoformat=lambda: '2024-01-01T00:00:00'))
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        response = self.client.get('/api/v1/users/1', headers={'x-access-token': MOCK_TOKEN})
        self.assertEqual(response.status_code, 200)
        self.assertIn('email_address', response.json)

    @patch('blueprints.users.users.db_connect')
    def test_get_user_not_found(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        response = self.client.get('/api/v1/users/1', headers={'x-access-token': MOCK_TOKEN})
        self.assertEqual(response.status_code, 404)

    @patch('blueprints.users.users.db_connect')
    def test_get_user_db_error(self, mock_db):
        mock_conn = MagicMock()
        mock_conn.cursor.side_effect = Exception("DB Error")
        mock_db.return_value = mock_conn

        response = self.client.get('/api/v1/users/1', headers={'x-access-token': MOCK_TOKEN})
        self.assertEqual(response.status_code, 500)

    # PUT /api/v1/users/<user_id>
    @patch('blueprints.users.users.db_connect')
    @patch('blueprints.users.users.valid_email', return_value=True)
    @patch('blueprints.users.users.valid_password', return_value=True)
    def test_update_user_success(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        payload = {"first_name": "Jane", "email_address": "jane@example.com", "password": "Password1!"}
        response = self.client.put('/api/v1/users/1', headers={'x-access-token': MOCK_TOKEN}, json=payload)
        self.assertEqual(response.status_code, 200)

    def test_update_user_no_data(self):
        response = self.client.put('/api/v1/users/1', headers={'x-access-token': MOCK_TOKEN}, json={})
        self.assertEqual(response.status_code, 400)

    @patch('blueprints.users.users.db_connect')
    def test_update_user_not_found(self, mock_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 0
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        payload = {"first_name": "NewName"}
        response = self.client.put('/api/v1/users/1', headers={'x-access-token': MOCK_TOKEN}, json=payload)
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()