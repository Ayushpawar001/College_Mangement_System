"""Run once to create users table on Supabase."""
import hashlib

import psycopg2

from config import DATABASE_URL

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Add it to the .env file or environment before running this script.")

conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cur = conn.cursor()

cur.execute(
    """
CREATE TABLE IF NOT EXISTS users (
    user_id    SERIAL PRIMARY KEY,
    username   VARCHAR(100) UNIQUE NOT NULL,
    email      VARCHAR(150) UNIQUE NOT NULL,
    password   VARCHAR(256) NOT NULL,
    role       VARCHAR(20) DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
)

default_password = hashlib.sha256("Admin@2026".encode()).hexdigest()
cur.execute(
    """
INSERT INTO users (username, email, password, role)
VALUES ('admin', 'admin@prmceam.com', %s, 'admin')
ON CONFLICT (username) DO NOTHING;
""",
    (default_password,),
)

conn.commit()

cur.execute("SELECT user_id, username, email, role FROM users")
users = cur.fetchall()
print("Users table created!")
print("Default credentials:")
print("  Username : admin")
print("  Password : Admin@2026")
print("
All users:", users)

cur.close()
conn.close()
