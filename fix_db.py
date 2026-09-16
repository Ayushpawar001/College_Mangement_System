"""Fix Supabase tables - drop and recreate with correct schema."""
import psycopg2

DATABASE_URL = "postgresql://postgres:Ayushpawar01@db.jybtewrvrefiuanxdxdj.supabase.co:5432/postgres"

conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cur = conn.cursor()

# Check existing students columns
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='students' ORDER BY ordinal_position")
cols = [r[0] for r in cur.fetchall()]
print("Current students columns:", cols)

# Drop all tables and recreate with correct schema
cur.execute("""
    DROP TABLE IF EXISTS fees CASCADE;
    DROP TABLE IF EXISTS marks CASCADE;
    DROP TABLE IF EXISTS attendance CASCADE;
    DROP TABLE IF EXISTS courses CASCADE;
    DROP TABLE IF EXISTS teachers CASCADE;
    DROP TABLE IF EXISTS events CASCADE;
    DROP TABLE IF EXISTS students CASCADE;
""")

cur.execute("""
CREATE TABLE students (
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

CREATE TABLE teachers (
    teacher_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    subject VARCHAR(100),
    phone VARCHAR(15),
    email VARCHAR(100)
);

CREATE TABLE courses (
    course_id SERIAL PRIMARY KEY,
    course_name VARCHAR(100),
    duration INT,
    fees DECIMAL(10,2)
);

CREATE TABLE attendance (
    attendance_id SERIAL PRIMARY KEY,
    student_id INT,
    attendance_date DATE,
    status VARCHAR(20),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

CREATE TABLE marks (
    mark_id SERIAL PRIMARY KEY,
    student_id INT,
    subject VARCHAR(100),
    marks DECIMAL(5,2),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

CREATE TABLE fees (
    fee_id SERIAL PRIMARY KEY,
    student_id INT,
    amount DECIMAL(10,2),
    payment_date DATE,
    status VARCHAR(20),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    event_date DATE NOT NULL,
    description VARCHAR(255)
);
""")

conn.commit()

# Verify all columns
for table in ['students', 'teachers', 'courses', 'attendance', 'marks', 'fees', 'events']:
    cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table}' ORDER BY ordinal_position")
    cols = [r[0] for r in cur.fetchall()]
    print(f"  {table}: {cols}")

cur.close()
conn.close()
print("All tables recreated successfully!")
