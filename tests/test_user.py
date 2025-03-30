import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from datetime import datetime
from blueprints.users.users import users_bp  # Adjust the import to reflect the directory structure

# Mocked data for the user
USER_EMAIL = 'jane.doe@example.com'
MOCK_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiODMiLCJhZG1pbiI6ZmFsc2UsImVtYWlsX2FkZHJlc3MiOiJqYW5lLmRvZUBleGFtcGxlLmNvbSIsImV4cCI6MTk0MzM0NjcxMX0.XEzFRK_e9WBrArWxAJBg19QSVfWM1iOB_Sga7_4NpmQ'

class UsersTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(users_bp)
        self.client = self.app.test_client()

    @patch('blueprints.users.users.db_connect')
    def test_get_user_success(self, mock_db_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Ensure the mock data structure matches what the application expects
        mock_cursor.fetchone.return_value = (
            1,  # user_id
            USER_EMAIL,  # email_address
            'Jane',  # first_name
            'Doe',  # last_name
            '0987654321',  # mobile_number
            'Paris',  # city
            False,  # admin
            datetime(2025, 3, 30, 15, 28, 31, 900241)  # creation_time as a datetime object
        )

        response = self.client.get('/api/v1/users/1', headers={'x-access-token': MOCK_TOKEN})

        # Check if the response is successful
        self.assertEqual(response.status_code, 200)

        # Check if the response contains the expected data
        response_data = response.json
        self.assertIn('email_address', response_data)
        self.assertEqual(response_data['email_address'], USER_EMAIL)
        self.assertEqual(response_data['user_id'], 1)
        self.assertEqual(response_data['first_name'], 'Jane')
        self.assertEqual(response_data['last_name'], 'Doe')
        self.assertEqual(response_data['mobile_number'], '0987654321')
        self.assertEqual(response_data['city'], 'Paris')
        self.assertEqual(response_data['admin'], False)
        self.assertEqual(response_data['creation_time'], '2025-03-30T15:28:31.900241')

    def test_get_user_not_found(self):
        response = self.client.get('/api/v1/users/999', headers={'x-access-token': MOCK_TOKEN})
        self.assertEqual(response.status_code, 404)

    def test_get_user_invalid_id(self):
        response = self.client.get('/api/v1/users/invalid_id', headers={'x-access-token': MOCK_TOKEN})
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
