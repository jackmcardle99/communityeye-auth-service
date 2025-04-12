"""
File: config.py
Author: Jack McArdle

This file is part of CommunityEye.

Email: mcardle-j9@ulster.ac.uk
B-No: B00733578
"""

from dotenv import load_dotenv
import os

load_dotenv()


DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')


FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
FLASK_DEBUG = os.getenv('FLASK_DEBUG')
FLASK_HOST = os.getenv('FLASK_HOST')
FLASK_PORT = int(os.getenv('FLASK_PORT'))