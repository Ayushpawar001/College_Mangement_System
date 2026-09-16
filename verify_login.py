"""Verify login credentials on Supabase."""
import hashlib
import psycopg2

DATABASE_URL = "postgresql://postgres:Ayushpawar01@db.jybtewrvrefiuanxdxdj.supabase.co:5432/postgres"

password = "Admin@2026"
hashed = hashlib.sha256(password.encode()).hexdigest()
print(f"Hash of Admin@2026: {hashed}")

conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cur = conn.cursor()

# Check what's in users table
cur.execute("SELECT user_id, username, email, password, role FROM users")
users = cur.fetchall()
print(f"\nUsers in Supabase:")
for u in users:
    print(f"  ID:{u[0]} | user:{u[1]} | email:{u[2]} | hash_match:{u[3]==hashed} | role:{u[4]}")

# Fix: update admin password hash
cur.execute("UPDATE users SET password=%s WHERE username='admin'", (hashed,))
conn.commit()
print("\nAdmin password hash updated on Supabase!")
print("Login with: admin / Admin@2026")

cur.close()
conn.close()
