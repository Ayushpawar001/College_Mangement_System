import os
import urllib.parse

from config import DATABASE_URL


def _is_mysql():
    """Check if we should use MySQL (local) or PostgreSQL (cloud)."""
    return DATABASE_URL.startswith("mysql://") or os.getenv("USE_MYSQL", "false").lower() == "true"


def get_connection():
    """Get database connection — MySQL locally, PostgreSQL on Render."""
    if _is_mysql():
        return _get_mysql_connection()
    return _get_pg_connection()


def _get_mysql_connection():
    """Connect to local MySQL."""
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="Ayushpawar01",
            database="college_db",
            port=3306,
            use_pure=True,
            auth_plugin="mysql_native_password"
        )
        return conn
    except Exception as e:
        print("MySQL connection error:", e)
        return None


def _get_pg_connection():
    """Connect to PostgreSQL (Supabase / Render)."""
    try:
        import pg8000.dbapi
        r = urllib.parse.urlparse(DATABASE_URL)
        params = {
            "host":     r.hostname,
            "port":     r.port or 5432,
            "user":     urllib.parse.unquote(r.username or "postgres"),
            "password": urllib.parse.unquote(r.password or ""),
            "database": r.path.lstrip("/"),
            "timeout":  15,
            "ssl_context": True,
        }
        return pg8000.dbapi.connect(**params)
    except Exception as e:
        print("Database connection error:", e)
        return None


def execute_query(query, values=None):
    """Execute INSERT, UPDATE, DELETE queries."""
    # Convert PostgreSQL %s to MySQL %s (same, no change needed)
    connection = get_connection()
    if connection is None:
        return False
    cursor = connection.cursor()
    try:
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
