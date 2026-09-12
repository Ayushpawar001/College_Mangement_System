from database import get_connection

connection = get_connection()

if connection:
    print("MySQL Connected Successfully!")

    connection.close()

else:
    print("Connection Failed!")