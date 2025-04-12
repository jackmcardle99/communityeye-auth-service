"""
File: db.py
Author: Jack McArdle

This file is part of CommunityEye.

Email: mcardle-j9@ulster.ac.uk
B-No: B00733578
"""

import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database() -> None:
    """
    Initialize the database by creating it if it doesn't exist and applying Flyway migrations.

    This function connects to the PostgreSQL server, checks if the database exists,
    creates it if necessary, and then applies any pending Flyway migrations.

    Raises:
        psycopg2.Error: If there is an error connecting to the PostgreSQL server.
    """
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        cursor.execute(
            f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'"
        )
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            logger.info(f"Database '{DB_NAME}' created successfully.")
        else:
            logger.info(
                f"Database '{DB_NAME}' already exists. Skipping creation."
            )

        cursor.close()
        conn.close()

        apply_flyway_migrations()

    except psycopg2.Error as e:
        logger.error(f"Error connecting to PostgreSQL: {e}")


def apply_flyway_migrations() -> None:
    """
    Apply Flyway migrations to the database.

    This function runs the Flyway migration command to apply any pending migrations
    to the database.

    Raises:
        subprocess.CalledProcessError: If the Flyway migration command fails.
    """
    flyway_command = ["flyway", "-configFiles=flyway.conf", "migrate"]
    try:
        subprocess.run(flyway_command, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Flyway migration failed: {e}")


def db_connect() -> psycopg2.connect:
    """
    Establish a connection to the PostgreSQL database.

    Returns:
        psycopg2.connect: A connection object to interact with the database.
    """
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST
    )
    return conn
