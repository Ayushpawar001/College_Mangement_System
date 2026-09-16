import urllib.parse
import pg8000.dbapi
from config import DATABASE_URL


def _get_conn_params():
    """Parse DATABASE_URL into connection parameters."""
    r = urllib.parse.urlparse(DATABASE_URL)
    return {
        "host":     r.hostname,
        "port":     r.port or 5432,
        "user":     r.username,
        "password": r.password,
        "database": r.path.lstrip("/"),
        "ssl_context": True,
    }


def get_connection():
    """Get PostgreSQL connection."""
    try:
        conn = pg8000.dbapi.connect(**_get_conn_params())
        return conn
    except Exception as e:
        print("Database connection error:", e)
        return None


def execute_query(query, values=None):
    """Execute INSERT, UPDATE, DELETE queries."""
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
