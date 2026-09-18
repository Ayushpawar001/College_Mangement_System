import hashlib
from datetime import date
from functools import wraps

from flask import Flask, flash, redirect, render_template_string, request, session, url_for

from config import PORT, SECRET_KEY
from database import execute_query, fetch_all

app = Flask(__name__)
app.secret_key = SECRET_KEY


def init_db():
    """Auto-create all tables and default admin on startup."""
    execute_query("""
        CREATE TABLE IF NOT EXISTS users (
            user_id    SERIAL PRIMARY KEY,
            username   VARCHAR(100) UNIQUE NOT NULL,
            email      VARCHAR(150) UNIQUE NOT NULL,
            password   VARCHAR(256) NOT NULL,
            role       VARCHAR(20) DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    execute_query("""
        CREATE TABLE IF NOT EXISTS students (
            student_id SERIAL PRIMARY KEY,
            user_id    INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            name VARCHAR(100) NOT NULL,
            age INT, gender VARCHAR(20),
            course VARCHAR(100), year INT,
            phone VARCHAR(15), email VARCHAR(100), address VARCHAR(255)
        )
    """)
    execute_query("""
        CREATE TABLE IF NOT EXISTS teachers (
            teacher_id SERIAL PRIMARY KEY,
            user_id    INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            name VARCHAR(100) NOT NULL,
            subject VARCHAR(100), phone VARCHAR(15), email VARCHAR(100)
        )
    """)
    execute_query("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id SERIAL PRIMARY KEY,
            user_id   INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            course_name VARCHAR(100), duration INT, fees DECIMAL(10,2)
        )
    """)
    execute_query("""
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id SERIAL PRIMARY KEY,
            user_id       INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            student_id INT, attendance_date DATE, status VARCHAR(20),
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        )
    """)
    execute_query("""
        CREATE TABLE IF NOT EXISTS marks (
            mark_id  SERIAL PRIMARY KEY,
            user_id  INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            student_id INT, subject VARCHAR(100), marks DECIMAL(5,2),
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        )
    """)
    execute_query("""
        CREATE TABLE IF NOT EXISTS fees (
            fee_id   SERIAL PRIMARY KEY,
            user_id  INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            student_id INT, amount DECIMAL(10,2),
            payment_date DATE, status VARCHAR(20),
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        )
    """)
    execute_query("""
        CREATE TABLE IF NOT EXISTS events (
            event_id SERIAL PRIMARY KEY,
            user_id  INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            title VARCHAR(100) NOT NULL,
            event_date DATE NOT NULL, description VARCHAR(255)
        )
    """)
    # Add user_id column to existing tables if missing (migration)
    for table in ["students","teachers","courses","attendance","marks","fees","events"]:
        execute_query(f"""
            DO $$ BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='{table}' AND column_name='user_id'
                ) THEN
                    ALTER TABLE {table} ADD COLUMN user_id INT REFERENCES users(user_id) ON DELETE CASCADE;
                END IF;
            END $$
        """)
    # Create default admin user
    import hashlib
    default_pwd = hashlib.sha256("Admin@2026".encode()).hexdigest()
    execute_query("""
        INSERT INTO users (username, email, password, role)
        VALUES ('admin', 'admin@prmceam.com', %s, 'admin')
        ON CONFLICT (username) DO NOTHING
    """, (default_pwd,))
    print("Database initialized successfully!")


# Initialize DB on startup
try:
    init_db()
except Exception as e:
    print(f"DB init error: {e}")


# ─────────────────────────────────────────────
# CACHE CONTROL
# ─────────────────────────────────────────────
@app.after_request
def disable_browser_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    return response


# ─────────────────────────────────────────────
# AUTH HELPERS
# ─────────────────────────────────────────────
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to continue.")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ─────────────────────────────────────────────
# AUTH TEMPLATES
# ─────────────────────────────────────────────
AUTH_STYLE = """
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #081431 0%, #0f2460 50%, #1a0533 100%);
    font-family: "Segoe UI", Tahoma, sans-serif;
  }
  .auth-card {
    background: #101f43;
    border: 1px solid #203563;
    border-radius: 12px;
    padding: 40px 36px;
    width: 100%;
    max-width: 420px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
  }
  .auth-logo {
    text-align: center;
    margin-bottom: 28px;
  }
  .auth-logo .brand {
    color: #e83e9f;
    font-size: 28px;
    font-weight: 800;
    letter-spacing: 2px;
  }
  .auth-logo .sub {
    color: #a7b4d4;
    font-size: 11px;
    letter-spacing: 3px;
    margin-top: 4px;
  }
  h2 {
    color: #f8faff;
    font-size: 20px;
    margin-bottom: 6px;
    text-align: center;
  }
  .auth-subtitle {
    color: #a7b4d4;
    font-size: 13px;
    text-align: center;
    margin-bottom: 24px;
  }
  .form-group { margin-bottom: 16px; }
  label {
    display: block;
    color: #a7b4d4;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 6px;
    letter-spacing: 0.5px;
  }
  input[type=text], input[type=email], input[type=password] {
    width: 100%;
    padding: 11px 14px;
    background: #0d1b3e;
    border: 1px solid #2a3f6e;
    border-radius: 6px;
    color: #f8faff;
    font-size: 14px;
    outline: none;
    transition: border-color 0.2s;
  }
  input:focus { border-color: #7044f5; }
  .btn {
    width: 100%;
    padding: 12px;
    background: #7044f5;
    color: #fff;
    border: none;
    border-radius: 6px;
    font-size: 15px;
    font-weight: 700;
    cursor: pointer;
    margin-top: 8px;
    transition: background 0.2s;
  }
  .btn:hover { background: #5a34d4; }
  .auth-link {
    text-align: center;
    margin-top: 20px;
    color: #a7b4d4;
    font-size: 13px;
  }
  .auth-link a { color: #7044f5; text-decoration: none; font-weight: 600; }
  .auth-link a:hover { color: #e83e9f; }
  .flash-error {
    background: #3b0d1a;
    border: 1px solid #ef4444;
    color: #fca5a5;
    padding: 10px 14px;
    border-radius: 6px;
    margin-bottom: 16px;
    font-size: 13px;
  }
  .flash-success {
    background: #0d2e1f;
    border: 1px solid #10b981;
    color: #6ee7b7;
    padding: 10px 14px;
    border-radius: 6px;
    margin-bottom: 16px;
    font-size: 13px;
  }
  .divider {
    text-align: center;
    color: #4a5568;
    font-size: 12px;
    margin: 16px 0;
    position: relative;
  }
  .divider::before, .divider::after {
    content: "";
    position: absolute;
    top: 50%;
    width: 42%;
    height: 1px;
    background: #203563;
  }
  .divider::before { left: 0; }
  .divider::after { right: 0; }
  .default-creds {
    background: #0a1a35;
    border: 1px solid #1e3a5f;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 18px;
    font-size: 12px;
    color: #7dd3fc;
  }
  .default-creds span { color: #a7b4d4; }
</style>
"""

LOGIN_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Login — PRMCEAM</title>
  """ + AUTH_STYLE + """
</head>
<body>
  <div class="auth-card">
    <div class="auth-logo">
      <div class="brand">PRMCEAM</div>
      <div class="sub">COLLEGE MANAGEMENT SYSTEM</div>
    </div>
    <h2>Welcome Back</h2>
    <p class="auth-subtitle">Sign in to your account to continue</p>

    {% with messages = get_flashed_messages() %}
      {% for msg in messages %}
        <div class="flash-error">{{ msg }}</div>
      {% endfor %}
    {% endwith %}

    <div class="default-creds">
      <span>Default credentials →</span>
      Username: <strong>admin</strong> &nbsp;|&nbsp;
      Password: <strong>Admin@2026</strong>
    </div>

    <form method="post">
      <div class="form-group">
        <label>USERNAME</label>
        <input type="text" name="username" placeholder="Enter username" required autofocus>
      </div>
      <div class="form-group">
        <label>PASSWORD</label>
        <input type="password" name="password" placeholder="Enter password" required>
      </div>
      <button class="btn" type="submit">Sign In →</button>
    </form>

    <div class="auth-link">
      Don't have an account? <a href="{{ url_for('register') }}">Register here</a>
    </div>
  </div>
</body>
</html>
"""

REGISTER_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Register — PRMCEAM</title>
  """ + AUTH_STYLE + """
</head>
<body>
  <div class="auth-card">
    <div class="auth-logo">
      <div class="brand">PRMCEAM</div>
      <div class="sub">COLLEGE MANAGEMENT SYSTEM</div>
    </div>
    <h2>Create Account</h2>
    <p class="auth-subtitle">Register a new admin account</p>

    {% with messages = get_flashed_messages() %}
      {% for msg in messages %}
        <div class="{{ 'flash-success' if 'success' in msg.lower() or 'created' in msg.lower() else 'flash-error' }}">{{ msg }}</div>
      {% endfor %}
    {% endwith %}

    <form method="post">
      <div class="form-group">
        <label>USERNAME</label>
        <input type="text" name="username" placeholder="Choose a username" required autofocus>
      </div>
      <div class="form-group">
        <label>EMAIL</label>
        <input type="email" name="email" placeholder="Enter your email" required>
      </div>
      <div class="form-group">
        <label>PASSWORD</label>
        <input type="password" name="password" placeholder="Min 6 characters" required>
      </div>
      <div class="form-group">
        <label>CONFIRM PASSWORD</label>
        <input type="password" name="confirm_password" placeholder="Repeat password" required>
      </div>
      <button class="btn" type="submit">Create Account →</button>
    </form>

    <div class="auth-link">
      Already have an account? <a href="{{ url_for('login') }}">Sign in here</a>
    </div>
  </div>
</body>
</html>
"""

# ─────────────────────────────────────────────
# ENTITY CONFIG
# ─────────────────────────────────────────────
ENTITIES = {
    "students": {
        "label": "Students",
        "table": "students",
        "columns": ["student_id", "name", "age", "gender", "course", "year", "phone", "email", "address"],
        "form": ["name", "age", "gender", "course", "year", "phone", "email", "address"],
        "display_columns": ["name", "age", "gender", "course", "year", "phone", "email", "address"],
    },
    "teachers": {
        "label": "Teachers",
        "table": "teachers",
        "columns": ["teacher_id", "name", "subject", "phone", "email"],
        "form": ["name", "subject", "phone", "email"],
        "display_columns": ["name", "subject", "phone", "email"],
    },
    "courses": {
        "label": "Courses",
        "table": "courses",
        "columns": ["course_id", "course_name", "duration", "fees"],
        "form": ["course_name", "duration", "fees"],
        "display_columns": ["course_name", "duration", "fees"],
    },
    "attendance": {
        "label": "Attendance",
        "table": "attendance",
        "columns": ["attendance_id", "student_id", "attendance_date", "status"],
        "form": ["student_id", "attendance_date", "status"],
        "display_columns": ["name", "attendance_date", "status"],
    },
    "marks": {
        "label": "Marks",
        "table": "marks",
        "columns": ["mark_id", "student_id", "subject", "marks"],
        "form": ["student_id", "subject", "marks"],
        "display_columns": ["name", "subject", "marks"],
    },
    "fees": {
        "label": "Fees",
        "table": "fees",
        "columns": ["fee_id", "student_id", "amount", "payment_date", "status"],
        "form": ["student_id", "amount", "payment_date", "status"],
        "display_columns": ["name", "amount", "payment_date", "status"],
    },
}

# ─────────────────────────────────────────────
# MAIN APP TEMPLATE
# ─────────────────────────────────────────────
TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>College Management System</title>
    <style>
        :root { --ink:#172033; --muted:#64748b; --line:#d8dee9; --paper:#fff; --wash:#f4f6fa; --blue:#1459d9; --navy:#111b55; --cyan:#0b9bb5; }
        * { box-sizing:border-box; } body { margin:0; color:var(--ink); background:var(--wash); font:14px/1.45 "Segoe UI",Tahoma,sans-serif; }
        .shell { display:grid; grid-template-columns:190px 1fr; min-height:100vh; } aside { background:linear-gradient(180deg,#111653,#123bd0); color:#fff; padding:34px 18px 20px; display:flex; flex-direction:column; } .brand { text-align:center; margin-bottom:42px; } .brand-mark { color:#36b9f0; font-size:30px; line-height:1; } .brand strong { display:block; margin-top:14px; font-size:17px; letter-spacing:.04em; } .brand small { color:#6ed9ff; font-size:9px; letter-spacing:.1em; } .side-nav { display:grid; gap:8px; } .side-nav a { color:#dbeafe; padding:10px 12px; border-radius:4px; text-decoration:none; font-weight:600; } .side-nav a:hover,.side-nav a.active { background:#245be2; color:white; } .side-footer { margin-top:auto; color:#b8c9ff; text-align:center; font-size:10px; }
        .content { min-width:0; padding:26px 30px 40px; } .topbar { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:20px; } h1 { margin:0; font-size:30px; } .subtitle { color:var(--muted); margin:4px 0 0; } .today { color:var(--blue); font-weight:700; text-align:right; font-size:12px; } .today span { display:block; color:var(--muted); font-size:10px; text-transform:uppercase; }
        .tabs { display:flex; flex-wrap:wrap; border-bottom:1px solid #bdc6d7; margin-bottom:20px; } .tabs a { color:var(--ink); text-decoration:none; padding:10px 18px; border:1px solid #b8c2d2; border-bottom:0; background:#dce3ef; } .tabs a:first-child { border-radius:4px 0 0 0; } .tabs a.active { color:white; background:var(--blue); border-color:var(--blue); font-weight:700; }
        .welcome, section, .stat { background:var(--paper); border:1px solid var(--line); border-radius:3px; } .welcome { padding:18px 20px; margin-bottom:18px; } h2 { margin:0 0 4px; font-size:20px; } .welcome p { color:var(--muted); margin:0; } .stats { display:grid; grid-template-columns:repeat(6,1fr); gap:10px; margin-bottom:22px; } .stat { padding:14px 16px; border-top:3px solid var(--cyan); } .stat strong { display:block; color:var(--blue); font-size:25px; } .stat span { color:var(--muted); font-size:12px; }
        .quick { padding:18px 20px; margin-bottom:18px; } .quick h3,.status h3 { color:var(--blue); margin:0 0 12px; font-size:13px; } .actions { display:flex; flex-wrap:wrap; gap:10px; } button { border:0; border-radius:2px; padding:10px 16px; color:white; background:var(--blue); font:600 13px inherit; cursor:pointer; } button:hover { background:#0c43ac; } .status { padding:18px 20px; min-height:135px; } .status p { color:var(--muted); margin:0; }
        .grid { display:grid; grid-template-columns:minmax(260px,340px) 1fr; gap:20px; align-items:start; } section { padding:20px; } label { display:block; margin:12px 0 5px; color:var(--muted); font-size:13px; font-weight:600; } input { width:100%; border:1px solid #cfd5df; border-radius:3px; padding:10px; font:inherit; } table { width:100%; border-collapse:collapse; display:block; overflow-x:auto; white-space:nowrap; } th,td { text-align:left; padding:11px 12px; border-bottom:1px solid var(--line); } th { color:var(--muted); font-size:12px; text-transform:uppercase; } .delete { margin:0; padding:5px 8px; background:#c93545; font-size:12px; } .flash { background:#e4f6ed; border:1px solid #a8dfc1; color:#17643b; padding:10px 14px; border-radius:3px; margin-bottom:18px; }
        @media (max-width:900px) { .stats { grid-template-columns:repeat(3,1fr); } } @media (max-width:650px) { .shell { display:block; } aside { padding:18px; } .brand { margin-bottom:15px; } .side-nav { grid-template-columns:repeat(3,1fr); } .side-footer { display:none; } .content { padding:20px 14px; } .topbar { gap:14px; } h1 { font-size:25px; } .stats { grid-template-columns:repeat(2,1fr); } }
    </style>
    <style>
        :root { --app-bg:#081431; --panel:#101f43; --purple:#7044f5; --pink:#e83e9f; --cyan:#1995ff; --green:#10e981; --text:#f8faff; --muted:#a7b4d4; --border:#203563; }
        body { background:var(--app-bg); color:var(--text); font-family:"Segoe UI",Tahoma,sans-serif; }
        .shell { grid-template-columns:200px 1fr; }
        aside { background:#07122e; padding:24px 14px 18px; }
        .brand { margin-bottom:34px; } .brand-mark { color:var(--pink); font-size:0; }
        .brand-mark::after { content:"PRMCEAM"; font-size:25px; font-weight:800; }
        .brand strong { margin-top:10px; font-size:20px; } .brand small { color:#a7b4d4; font-size:10px; }
        .side-nav { gap:7px; } .side-nav a { color:var(--muted); border-radius:0; padding:13px 14px; }
        .side-nav a:hover,.side-nav a.active { background:var(--purple); color:#fff; }
        .side-footer { background:#1a2945; padding:18px 8px; color:#dbeafe; }
        .content { padding:26px 16px 28px; } .topbar { margin:0 4px 18px; }
        h1 { font-size:28px; color:#fff; } .subtitle { color:var(--muted); }
        .today { color:#dbeafe; } .today span { display:none; }
        .tabs { margin:0 0 8px; border-bottom:2px solid #263b6e; }
        .tabs a { color:#dbeafe; background:#142753; border-color:#7180a4; padding:10px 18px; }
        .tabs a.active { background:var(--purple); border-color:var(--purple); }
        .welcome { background:transparent; border:0; padding:0; margin:0; height:0; overflow:hidden; }
        .stats { grid-template-columns:repeat(6,1fr); gap:10px; margin:0 0 14px; }
        .stat { background:var(--panel); border:1px solid var(--border); border-top:3px solid var(--purple); border-radius:0; padding:16px; min-height:108px; }
        .stat:nth-child(2) { border-top-color:var(--cyan); } .stat:nth-child(3) { border-top-color:#f59e0b; }
        .stat:nth-child(4) { border-top-color:var(--pink); } .stat:nth-child(5) { border-top-color:var(--green); }
        .stat:nth-child(6) { border-top-color:#f59e0b; } .stat strong { color:#fff; font-size:27px; }
        .stat span { color:var(--muted); } .stat small { display:block; color:var(--muted); margin-top:10px; font-size:10px; }
        .dashboard-grid { display:grid; grid-template-columns:1.35fr .8fr 1.35fr; gap:10px; }
        .dashboard-panel { background:var(--panel); border:1px solid var(--border); padding:16px; min-height:284px; }
        .dashboard-panel h3 { margin:0 0 5px; font-size:15px; } .dashboard-panel p { color:var(--muted); margin:0; font-size:12px; }
        .bar-chart { display:flex; align-items:flex-end; gap:6px; height:150px; margin-top:16px; padding:0 4px 0 8px; border-bottom:2px solid #284475; border-left:2px solid #284475; }
        .bar-chart .bar-col { flex:1; display:flex; flex-direction:column; align-items:center; gap:3px; height:100%; justify-content:flex-end; }
        .bar-chart .bar-fill { width:80%; background:var(--green); border-radius:2px 2px 0 0; min-height:3px; transition:height 0.5s; }
        .bar-chart .bar-pct { font-size:9px; color:#a7b4d4; }
        .bar-chart .bar-date { font-size:9px; color:#a7b4d4; white-space:nowrap; }
        .no-data-msg { display:flex; align-items:center; justify-content:center; height:150px; color:#a7b4d4; font-size:13px; }
        .legend { text-align:center; color:var(--green)!important; }
        .quick,.status { background:var(--panel); border:1px solid var(--border); border-radius:0; padding:16px; margin-top:10px; }
        .quick h3,.status h3 { color:#fff; } .actions button { border-radius:0; }
        section { background:var(--panel); border-color:var(--border); border-radius:0; } label,input,select { color:var(--text); } input,select { background:#f8faff; color:#172033; }
        th { color:#dbeafe; background:#1a315f; } td { color:#dbeafe; } table { border:1px solid #7180a4; }
        @media (max-width:1100px) { .stats { grid-template-columns:repeat(3,1fr); } .dashboard-grid { grid-template-columns:1fr 1fr; } .dashboard-grid .dashboard-panel:first-child { grid-column:span 2; } }
        @media (max-width:650px) { .dashboard-grid { grid-template-columns:1fr; } .dashboard-grid .dashboard-panel:first-child { grid-column:auto; } }
        .topbar-copy h1 { margin-bottom:2px; } .topbar-copy .subtitle { margin:0; }
        .search-box { width:160px; border:0; border-radius:0; background:#13244b; color:#dbeafe; padding:10px; }
        .event-form { display:grid; grid-template-columns:1fr 120px auto; gap:8px; margin:10px 0 12px; }
        .event-form input { min-width:0; border:2px solid #b8c2d2; border-radius:0; padding:8px; }
        .event-form input[name="description"] { grid-column:1 / 3; }
        .event-button { border-radius:0; padding:10px 16px; } .event-add { background:#10b981; }
        .event-update { background:#7044f5; } .event-delete { background:#ef4444; }
        .events-table th,.events-table td { padding:8px 10px; } .events-table td:last-child { white-space:normal; }
        .attendance-key { color:var(--green)!important; font-weight:700; text-align:left; margin-top:8px!important; }
        .attendance-key::before { content:"●"; margin-right:8px; } .attendance-absent { color:#ff4f86!important; }
        .entity-actions { display:flex; gap:8px; margin-top:16px; }
        .entity-actions button { border-radius:0; } .entity-update { background:#7044f5; }
        .entity-delete { background:#ef4444; }
        .internal-id { display:none; }
        .entity-clear { background:#64748b; } .entity-row { cursor:pointer; }
        .logout-btn { display:block; margin:10px 12px 0; padding:10px 14px; background:#ef4444; color:#fff; text-align:center; text-decoration:none; font-weight:700; font-size:13px; border-radius:0; }
        .logout-btn:hover { background:#c53030; }
        .user-info { padding:10px 14px; color:#a7b4d4; font-size:12px; border-top:1px solid #203563; margin-top:8px; }
    </style>
</head>
<body><div class="shell"><aside>
  <div class="brand"><div class="brand-mark">◆</div><strong>COLLEGE</strong><small>MANAGEMENT SYSTEM</small></div>
  <nav class="side-nav">
    <a class="{{ 'active' if section == 'dashboard' else '' }}" href="{{ url_for('dashboard') }}">Dashboard</a>
    {% for key, item in entities.items() %}
    <a class="{{ 'active' if key == section else '' }}" href="{{ url_for('dashboard', section=key) }}">{{ item.label }}</a>
    {% endfor %}
  </nav>
  <div class="user-info">👤 {{ session.get('username', 'Admin') }}</div>
  <a class="logout-btn" href="{{ url_for('logout') }}">⏻ Logout</a>
  <div class="side-footer">College Management System<br>&copy; 2026</div>
</aside><main class="content">
<div class="topbar">
  <div class="topbar-copy">
    <h1>{{ 'Welcome back, ' + session.get('username','Admin') + '!' if section == 'dashboard' else entity.label }}</h1>
    <p class="subtitle">{{ "Here's what's happening in your college today." if section == 'dashboard' else 'Manage your college activities from one place' }}</p>
  </div>
  {% if section == 'dashboard' %}
  <div style="display:flex;align-items:center;gap:20px">
    <input class="search-box" type="search" placeholder="Search anything...">
    <div class="today">{{ today }}</div>
  </div>
  {% else %}
  <div class="today">{{ today }}</div>
  {% endif %}
</div>
{% with messages = get_flashed_messages() %}{% for message in messages %}<div class="flash">{{ message }}</div>{% endfor %}{% endwith %}
<nav class="tabs">
  <a class="{{ 'active' if section == 'dashboard' else '' }}" href="{{ url_for('dashboard') }}">Dashboard</a>
  {% for key, item in entities.items() %}
  <a class="{{ 'active' if key == section else '' }}" href="{{ url_for('dashboard', section=key) }}">{{ item.label }}</a>
  {% endfor %}
</nav>
{% if section == 'dashboard' %}
<div class="stats">{% for key, item in counts.items() %}<div class="stat"><strong>{% if key == 'fees' %}Rs {{ '{:,.0f}'.format(fee_total) }}{% else %}{{ item }}{% endif %}</strong><span>{% if key == 'fees' %}Total Fees Collected{% else %}Total {{ entities[key].label }}{% endif %}</span><small>{% if key == 'fees' %}Live database total{% else %}Live database count{% endif %}</small></div>{% endfor %}</div>
<div class="dashboard-grid">
  <div class="dashboard-panel"><h3>Attendance overview</h3><p>Last 7 days performance</p>
  {% if weekly_attendance %}
  <div class="bar-chart">
    {% for row in weekly_attendance %}
    {% set pct = ((row[1] * 100) / row[3])|round|int if row[3] else 0 %}
    <div class="bar-col">
      <div class="bar-pct">{{ pct }}%</div>
      <div class="bar-fill" style="height:{{ pct }}%;"></div>
      <div class="bar-date">{{ row[0].strftime('%d/%m') if row[0] else '' }}</div>
    </div>
    {% endfor %}
  </div>
  {% else %}
  <div class="no-data-msg">No attendance data yet</div>
  {% endif %}
  </div>
  <div class="dashboard-panel"><h3>Today's attendance</h3>
  <div style="position:relative;width:160px;height:160px;margin:16px auto 8px;">
    <svg viewBox="0 0 160 160" width="160" height="160">
      <circle cx="80" cy="80" r="60" fill="none" stroke="#23477f" stroke-width="22"/>
      <circle cx="80" cy="80" r="60" fill="none" stroke="#10e981" stroke-width="22"
        stroke-dasharray="{{ (attendance_pct * 3.77)|round }} 377"
        stroke-dashoffset="94.25"
        stroke-linecap="butt"
        transform="rotate(-90 80 80)"/>
    </svg>
    <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;line-height:1.2;">
      <div style="font-size:26px;font-weight:800;color:#fff;">{{ attendance_pct }}%</div>
      <div style="font-size:10px;color:#a7b4d4;margin-top:2px;">Present</div>
    </div>
  </div>
  <p class="legend attendance-key" style="text-align:center;margin-top:6px;">● Present &nbsp; {{ present }}</p>
  <p class="legend attendance-key attendance-absent" style="text-align:center;margin-top:4px;">● Absent &nbsp; {{ absent }}</p>
  </div>
  <div class="dashboard-panel"><h3>Upcoming Events</h3><form class="event-form" method="post" action="{{ url_for('add_event') }}"><input name="title" placeholder="Title" required><input name="event_date" type="date" value="{{ today }}" required><input name="description" placeholder="Description"><button class="event-button event-add" type="submit">Add</button><button class="event-button event-update" type="button">Update</button><button class="event-button event-delete" type="reset">Delete</button></form><table class="events-table"><thead><tr><th>ID</th><th>Title</th><th>Date</th><th>Description</th></tr></thead><tbody>{% for event in events %}<tr><td>{{ event[0] }}</td><td>{{ event[1] }}</td><td>{{ event[2] }}</td><td>{{ event[3] }}</td></tr>{% else %}<tr><td colspan="4">No records found.</td></tr>{% endfor %}</tbody></table></div>
</div>
<div class="dashboard-panel" style="margin-top:10px"><h3>Recent Students</h3><p>Latest students in the database</p>{% if recent_students %}<table style="margin-top:12px"><thead><tr><th>ID</th><th>Name</th><th>Course</th><th>Year</th></tr></thead><tbody>{% for row in recent_students %}<tr>{% for value in row %}<td>{{ value }}</td>{% endfor %}</tr>{% endfor %}</tbody></table>{% else %}<p style="margin-top:18px">No student records found.</p>{% endif %}</div>
{% else %}
<div class="grid">
  <section><h2>Add {{ entity.label[:-1] if entity.label.endswith('s') else entity.label }}</h2>
  <form id="entity-form" data-entity="{{ section }}" method="post" action="{{ url_for('add_record', entity_name=section) }}">
  {% for field in entity.form %}
  <label for="{{ field }}">{{ 'Student Name' if field == 'student_id' else field.replace('_', ' ').title() }}</label>
  {% if field == 'student_id' %}
  <select id="{{ field }}" name="{{ field }}" required><option value="">Select student</option>{% for student_id, student_name in student_options %}<option value="{{ student_id }}">{{ student_name }}</option>{% endfor %}</select>
  {% elif field == 'status' %}
  <select id="{{ field }}" name="{{ field }}" required>{% if section == 'fees' %}<option value="Paid">Paid</option><option value="Pending">Pending</option>{% else %}<option value="Present">Present</option><option value="Absent">Absent</option>{% endif %}</select>
  {% else %}
  <input id="{{ field }}" name="{{ field }}" type="{{ 'date' if field.endswith('date') else ('number' if field in ['age', 'year', 'duration'] else 'text') }}" value="{{ today if field.endswith('date') else '' }}" {{ 'required' if field in ['name','course_name','attendance_date','subject'] else '' }}>
  {% endif %}
  {% endfor %}
  <div class="entity-actions"><button type="submit">Add record</button><button class="entity-update" type="button">Update</button><button class="entity-delete" type="button" disabled>Delete</button><button class="entity-clear" type="reset">Clear</button></div>
  </form></section>
  <section><h2>{{ entity.label }}</h2>{% if rows %}<table class="entity-table"><thead><tr><th class="internal-id">Record</th>{% for column in entity.display_columns %}<th>{{ column.replace('_', ' ').title() }}</th>{% endfor %}<th>Action</th></tr></thead><tbody>{% for row in display_rows %}<tr class="entity-row" data-values='{{ rows[loop.index0][1:]|tojson }}'><td class="internal-id">{{ row[0] }}</td>{% for value in row[1:] %}<td>{{ value }}</td>{% endfor %}<td><form method="post" action="{{ url_for('delete_record', entity_name=section, record_id=row[0]) }}"><button class="delete" type="submit">Delete</button></form></td></tr>{% endfor %}</tbody></table>{% else %}<p>No records found.</p>{% endif %}</section>
</div>
{% endif %}
<script>
    const entityForm = document.querySelector('#entity-form');
    const entityRows = document.querySelectorAll('.entity-row');
    if (entityForm) {
        const entityUpdate = entityForm.querySelector('.entity-update');
        const entityDelete = entityForm.querySelector('.entity-delete');
        const entityAdd = entityForm.querySelector('button[type="submit"]');
        const entityFields = {{ entity.form|tojson if entity else '[]' }};
        const entityColumns = {{ entity.columns|tojson if entity else '[]' }};
        entityRows.forEach((row) => row.addEventListener('click', (event) => {
            if (event.target.closest('button')) return;
            const recordId = row.cells[0].textContent.trim();
            const rawValues = JSON.parse(row.dataset.values || '[]');
            entityFields.forEach((field) => {
                const columnIndex = entityColumns.indexOf(field) - 1;
                const input = entityForm.querySelector(`[name="${field}"]`);
                if (input && columnIndex >= 0) input.value = rawValues[columnIndex] ?? '';
            });
            entityForm.action = `/update/${entityForm.dataset.entity}/${recordId}`;
            entityUpdate.type = 'submit';
            entityDelete.disabled = false;
            entityDelete.onclick = () => {
                entityForm.action = `/delete/${entityForm.dataset.entity}/${recordId}`;
                entityForm.submit();
            };
            entityAdd.disabled = true;
            entityUpdate.focus();
        }));
    }
    const eventForm = document.querySelector('.event-form');
    const eventRows = document.querySelectorAll('.events-table tbody tr');
    if (eventForm) {
        const updateButton = eventForm.querySelector('.event-update');
        const addButton = eventForm.querySelector('.event-add');
        const titleInput = eventForm.querySelector('[name="title"]');
        const dateInput = eventForm.querySelector('[name="event_date"]');
        const descriptionInput = eventForm.querySelector('[name="description"]');
        const deleteButton = eventForm.querySelector('.event-delete');
        let selectedEventId = null;
        eventRows.forEach((row) => {
            if (row.cells.length < 4) return;
            row.style.cursor = 'pointer';
            row.addEventListener('click', () => {
                selectedEventId = row.cells[0].textContent.trim();
                titleInput.value = row.cells[1].textContent.trim();
                dateInput.value = row.cells[2].textContent.trim();
                descriptionInput.value = row.cells[3].textContent.trim();
                eventForm.action = `/events/update/${row.cells[0].textContent.trim()}`;
                updateButton.type = 'submit';
                addButton.disabled = true;
                updateButton.focus();
            });
        });
        deleteButton.type = 'button';
        deleteButton.addEventListener('click', () => {
            if (selectedEventId) window.location.href = `/events/delete/${selectedEventId}`;
        });
    }
</script>
</main></div></body></html>
"""


# ─────────────────────────────────────────────
# AUTH ROUTES
# ─────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Username and password are required.")
            return render_template_string(LOGIN_TEMPLATE)

        try:
            hashed = hash_password(password)
            print(f"LOGIN ATTEMPT: user={username} hash={hashed[:20]}...")
            user = fetch_all(
                "SELECT user_id, username, role FROM users WHERE username=%s AND password=%s",
                (username, hashed)
            )
            print(f"LOGIN RESULT: {user}")
        except Exception as e:
            print(f"LOGIN ERROR: {e}")
            flash(f"Database error: {e}")
            return render_template_string(LOGIN_TEMPLATE)

        if user:
            session["user_id"]  = user[0][0]
            session["username"] = user[0][1]
            session["role"]     = user[0][2]
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password. Please try again.")

    return render_template_string(LOGIN_TEMPLATE)


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username         = request.form.get("username", "").strip()
        email            = request.form.get("email", "").strip()
        password         = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not all([username, email, password, confirm_password]):
            flash("All fields are required.")
            return render_template_string(REGISTER_TEMPLATE)

        if len(password) < 6:
            flash("Password must be at least 6 characters.")
            return render_template_string(REGISTER_TEMPLATE)

        if password != confirm_password:
            flash("Passwords do not match.")
            return render_template_string(REGISTER_TEMPLATE)

        existing = fetch_all("SELECT user_id FROM users WHERE username=%s OR email=%s", (username, email))
        if existing:
            flash("Username or email already exists.")
            return render_template_string(REGISTER_TEMPLATE)

        success = execute_query(
            "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
            (username, email, hash_password(password), "admin")
        )

        if success:
            flash("Account created successfully! Please sign in.")
            return redirect(url_for("login"))
        else:
            flash("Registration failed. Please try again.")

    return render_template_string(REGISTER_TEMPLATE)


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
def _load_counts():
    uid = session.get("user_id")
    return {name: len(fetch_all(f"SELECT {item['columns'][0]} FROM {item['table']} WHERE user_id=%s", (uid,))) for name, item in ENTITIES.items()}


def _load_dashboard_data():
    uid = session.get("user_id")
    fee_total = fetch_all("SELECT COALESCE(SUM(amount), 0) FROM fees WHERE user_id=%s", (uid,))
    today_attendance = fetch_all(
        "SELECT status, COUNT(*) FROM attendance WHERE attendance_date=%s AND user_id=%s GROUP BY status",
        (date.today(), uid),
    )
    # Last 7 days attendance for bar chart
    weekly_attendance = fetch_all(
        """
        SELECT attendance_date,
               SUM(CASE WHEN LOWER(status)='present' THEN 1 ELSE 0 END) as present,
               SUM(CASE WHEN LOWER(status)='absent'  THEN 1 ELSE 0 END) as absent,
               COUNT(*) as total
        FROM attendance
        WHERE user_id=%s
          AND attendance_date >= CURRENT_DATE - INTERVAL '6 days'
        GROUP BY attendance_date
        ORDER BY attendance_date
        """,
        (uid,)
    )
    present = sum(count for status, count in today_attendance if str(status).lower() == "present")
    absent  = sum(count for status, count in today_attendance if str(status).lower() == "absent")
    return {
        "fee_total":         float(fee_total[0][0] or 0) if fee_total else 0,
        "present":           present,
        "absent":            absent,
        "attendance_pct":    round((present * 100) / (present + absent)) if present + absent else 0,
        "weekly_attendance": weekly_attendance,
        "events":            fetch_all("SELECT event_id, title, event_date, description FROM events WHERE user_id=%s ORDER BY event_date LIMIT 5", (uid,)),
    }


def _load_display_rows(entity_name, entity, rows):
    uid = session.get("user_id")
    if entity_name in {"attendance", "marks", "fees"}:
        table = entity["table"]
        linked_columns = ", ".join(f"{table}.{col}" for col in entity["form"] if col != "student_id")
        return fetch_all(
            f"SELECT {table}.{entity['columns'][0]}, students.name, {linked_columns} "
            f"FROM {table} JOIN students ON {table}.student_id = students.student_id "
            f"WHERE {table}.user_id=%s "
            f"ORDER BY {table}.{entity['columns'][0]} DESC",
            (uid,)
        )
    return [[row[0], *row[1:]] for row in rows]


# ─────────────────────────────────────────────
# PROTECTED ROUTES
# ─────────────────────────────────────────────
@app.get("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.get("/home")
@login_required
def dashboard():
    uid     = session.get("user_id")
    section = request.args.get("section", "dashboard")
    entity  = ENTITIES.get(section)
    rows, display_rows = [], []

    recent_students = fetch_all(
        "SELECT student_id, name, course, year FROM students WHERE user_id=%s ORDER BY student_id DESC LIMIT 5",
        (uid,)
    ) if section == "dashboard" else []

    student_options = fetch_all(
        "SELECT student_id, name FROM students WHERE user_id=%s ORDER BY name",
        (uid,)
    )
    dashboard_data = _load_dashboard_data() if section == "dashboard" else {"fee_total": 0, "present": 0, "absent": 0, "attendance_pct": 0, "weekly_attendance": [], "events": []}

    if entity:
        rows         = fetch_all(f"SELECT {', '.join(entity['columns'])} FROM {entity['table']} WHERE user_id=%s ORDER BY {entity['columns'][0]} DESC", (uid,))
        display_rows = _load_display_rows(section, entity, rows)

    return render_template_string(
        TEMPLATE,
        entities=ENTITIES,
        counts=_load_counts(),
        **dashboard_data,
        section=section,
        entity=entity,
        rows=rows,
        display_rows=display_rows,
        recent_students=recent_students,
        student_options=student_options,
        today=date.today().isoformat(),
    )


@app.post("/events/add")
@login_required
def add_event():
    uid = session.get("user_id")
    execute_query(
        "INSERT INTO events (user_id, title, event_date, description) VALUES (%s, %s, %s, %s)",
        (uid, request.form.get("title", "").strip(), request.form.get("event_date", ""), request.form.get("description", "").strip()),
    )
    return redirect(url_for("dashboard"))


@app.route("/events/delete/<int:event_id>", methods=["GET", "POST"])
@login_required
def delete_event(event_id):
    uid = session.get("user_id")
    execute_query("DELETE FROM events WHERE event_id=%s AND user_id=%s", (event_id, uid))
    return redirect(url_for("dashboard"))


@app.post("/events/update/<int:event_id>")
@login_required
def update_event(event_id):
    uid = session.get("user_id")
    execute_query(
        "UPDATE events SET title=%s, event_date=%s, description=%s WHERE event_id=%s AND user_id=%s",
        (request.form.get("title", "").strip(), request.form.get("event_date", ""), request.form.get("description", "").strip(), event_id, uid),
    )
    return redirect(url_for("dashboard"))


@app.post("/add/<entity_name>")
@login_required
def add_record(entity_name):
    if entity_name not in ENTITIES:
        return redirect(url_for("dashboard"))
    uid    = session.get("user_id")
    entity = ENTITIES[entity_name]
    values = [request.form.get(field, "").strip() for field in entity["form"]]
    # Insert with user_id
    fields_with_uid = ["user_id"] + entity["form"]
    values_with_uid = [uid] + values
    if not execute_query(
        f"INSERT INTO {entity['table']} ({', '.join(fields_with_uid)}) VALUES ({', '.join(['%s'] * len(values_with_uid))})",
        values_with_uid,
    ):
        flash("The record could not be added. Check the database connection and values.")
    else:
        flash(f"{entity['label'][:-1]} added successfully.")
    return redirect(url_for("dashboard", section=entity_name))


@app.post("/delete/<entity_name>/<int:record_id>")
@login_required
def delete_record(entity_name, record_id):
    if entity_name in ENTITIES:
        uid    = session.get("user_id")
        entity = ENTITIES[entity_name]
        execute_query(
            f"DELETE FROM {entity['table']} WHERE {entity['columns'][0]}=%s AND user_id=%s",
            (record_id, uid)
        )
        flash("Record deleted.")
    return redirect(url_for("dashboard", section=entity_name))


@app.post("/update/<entity_name>/<int:record_id>")
@login_required
def update_record(entity_name, record_id):
    if entity_name not in ENTITIES:
        return redirect(url_for("dashboard"))
    uid    = session.get("user_id")
    entity = ENTITIES[entity_name]
    values = [request.form.get(field, "").strip() for field in entity["form"]]
    assignments = ", ".join(f"{field} = %s" for field in entity["form"])
    if execute_query(
        f"UPDATE {entity['table']} SET {assignments} WHERE {entity['columns'][0]}=%s AND user_id=%s",
        (*values, record_id, uid),
    ):
        flash(f"{entity['label'][:-1]} updated successfully.")
    else:
        flash("The record could not be updated.")
    return redirect(url_for("dashboard", section=entity_name))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
