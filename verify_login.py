"""Verify login credentials on Supabase."""
import hashlib

import psycopg2

from config import DATABASE_URL

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Add it to the .env file or environment before running this script.")

password = "Admin@2026"
hashed = hashlib.sha256(password.encode()).hexdigest()
print(f"Hash of Admin@2026: {hashed}")

conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cur = conn.cursor()

cur.execute("SELECT user_id, username, email, password, role FROM users")
users = cur.fetchall()
print("
Users in Supabase:")
for user in users:
    print(f"  ID:{user[0]} | user:{user[1]} | email:{user[2]} | hash_match:{user[3] == hashed} | role:{user[4]}")

cur.execute("UPDATE users SET password = %s WHERE username = 'admin'", (hashed,))
conn.commit()
print("
Admin password hash updated on Supabase!")
print("Login with: admin / Admin@2026")

cur.close()
conn.close()
