"""
Run this script once to create all tables on Supabase PostgreSQL.
Usage: python setup_db.py
"""
import psycopg2

DATABASE_URL = "postgresql://postgres:Ayushpawar01@db.jybtewrvrefiuanxdxdj.supabase.co:5432/postgres"

SQL = """
CREATE TABLE IF NOT EXISTS students (
    student_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT,
    gender VARCHAR(20),
    course VARCHAR(100),
    year INT,
    phone VARCHAR(15),
    email VARCHAR(100),
    address VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS teachers (
    teacher_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    subject VARCHAR(100),
    phone VARCHAR(15),
    email VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS courses (
    course_id SERIAL PRIMARY KEY,
    course_name VARCHAR(100),
    duration INT,
    fees DECIMAL(10,2)
);

CREATE TABLE IF NOT EXISTS attendance (
    attendance_id SERIAL PRIMARY KEY,
    student_id INT,
    attendance_date DATE,
    status VARCHAR(20),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS marks (
    mark_id SERIAL PRIMARY KEY,
    student_id INT,
    subject VARCHAR(100),
    marks DECIMAL(5,2),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS fees (
    fee_id SERIAL PRIMARY KEY,
    student_id INT,
    amount DECIMAL(10,2),
    payment_date DATE,
    status VARCHAR(20),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS events (
    event_id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    event_date DATE NOT NULL,
    description VARCHAR(255)
);
"""

try:
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    cur = conn.cursor()
    cur.execute(SQL)
    conn.commit()

    # Verify tables
    cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
    tables = cur.fetchall()
    print("✅ Tables created successfully:")
    for t in tables:
        print(f"   - {t[0]}")

    cur.close()
    conn.close()
    print("✅ Supabase connection OK!")

except Exception as e:
    print(f"❌ Error: {e}")
