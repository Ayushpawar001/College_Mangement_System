import os
import psycopg2
from psycopg2 import OperationalError

from config import DATABASE_URL


def get_connection():
    """Get PostgreSQL connection using Supabase DATABASE_URL."""
    try:
        connection = psycopg2.connect(DATABASE_URL, sslmode="require")
        return connection
    except OperationalError as e:
        print("Database connection error:", e)
        return None


def execute_query(query, values=None):
    """Execute INSERT, UPDATE, DELETE queries."""
    connection = get_connection()

    if connection is None:
        return False

    cursor = connection.cursor()

    try:
        # Convert MySQL %s placeholders — psycopg2 also uses %s so no change needed
        cursor.execute(query, values or ())
        connection.commit()
        return True

    except Exception as e:
        print("Database error:", e)
        connection.rollback()
        return False

    finally:
        cursor.close()
        connection.close()


def fetch_all(query, values=None):
    """Execute SELECT queries and return all rows."""
    connection = get_connection()

    if connection is None:
        return []

    cursor = connection.cursor()

    try:
        cursor.execute(query, values or ())
        return cursor.fetchall()

    except Exception as e:
        print("Database error:", e)
        return []

    finally:
        cursor.close()
        connection.close()
