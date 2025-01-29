import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def init_database():
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(dbname='postgres', user='communityeye', password='communityeye', host='localhost')
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if the database exists
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'communityeye'")
        exists = cursor.fetchone()

        if not exists:
            cursor.execute('CREATE DATABASE communityeye')
            print("Database 'communityeye' created successfully.")
        else:
            print("Database 'communityeye' already exists. Skipping creation")

        cursor.close()
        conn.close()

        # Apply Flyway migrations
        apply_flyway_migrations()

    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")


def apply_flyway_migrations():
    flyway_command = ['flyway', '-configFiles=flyway.conf', 'migrate']
    try:
        subprocess.run(flyway_command, check=True)        
    except subprocess.CalledProcessError as e:
        print(f"Flyway migration failed: {e}")


def db_connect():
   conn = psycopg2.connect(dbname='communityeye', user='communityeye', password='communityeye', host='localhost')
   return conn