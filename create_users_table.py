"""Run once to create users table on Supabase."""
import psycopg2
import hashlib

DATABASE_URL = "postgresql://postgres:Ayushpawar01@db.jybtewrvrefiuanxdxdj.supabase.co:5432/postgres"

conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cur = conn.cursor()

# Create users table
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id    SERIAL PRIMARY KEY,
    username   VARCHAR(100) UNIQUE NOT NULL,
    email      VARCHAR(150) UNIQUE NOT NULL,
    password   VARCHAR(256) NOT NULL,
    role       VARCHAR(20) DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# Create default admin user (password: Admin@2026)
default_password = hashlib.sha256("Admin@2026".encode()).hexdigest()
cur.execute("""
INSERT INTO users (username, email, password, role)
VALUES ('admin', 'admin@prmceam.com', %s, 'admin')
ON CONFLICT (username) DO NOTHING;
""", (default_password,))

conn.commit()

cur.execute("SELECT user_id, username, email, role FROM users")
users = cur.fetchall()
print("Users table created!")
print("Default credentials:")
print("  Username : admin")
print("  Password : Admin@2026")
print("\nAll users:", users)

cur.close()
conn.close()
