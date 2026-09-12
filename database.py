import mysql.connector
from mysql.connector import Error

from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT, DB_SSL


def get_connection():

    try:
        connect_args = dict(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            use_pure=True,
        )

        # Use SSL for cloud databases (e.g. Render, PlanetScale, Aiven)
        if DB_SSL:
            connect_args["ssl_disabled"] = False
        else:
            connect_args["auth_plugin"] = "mysql_native_password"

        connection = mysql.connector.connect(**connect_args)

        return connection

    except Error as e:

        print("Database connection error:", e)

        return None


def execute_query(query, values=None):

    connection = get_connection()

    if connection is None:
        return False

    cursor = connection.cursor()

    try:

        cursor.execute(query, values or ())
        connection.commit()

        return True

    except Error as e:

        print("Database error:", e)
        connection.rollback()

        return False

    finally:

        cursor.close()
        connection.close()


def fetch_all(query, values=None):

    connection = get_connection()

    if connection is None:
        return []

    cursor = connection.cursor()

    try:

        cursor.execute(query, values or ())

        return cursor.fetchall()

    except Error as e:

        print("Database error:", e)

        return []

    finally:

        cursor.close()
        connection.close()
