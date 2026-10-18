# 🎓 PRMCEAM - College Management System

A full-featured College Management System built with **Python** and **Flask**, connected to **MySQL** database, with full authentication and hosted on **Render**.

---

## 📋 Features

| Module | Description |
|---|---|
| 🔐 Authentication | Login / Register / Logout per user |
| 🎓 Students | Add, update, delete, view student records |
| 👨‍🏫 Teachers | Manage teacher information |
| 📚 Courses | Manage course details and fees |
| ✅ Attendance | Mark and track student attendance |
| 📝 Marks | Record and view student marks |
| 💰 Fees | Track fee payments and status |
| 📅 Events | Add and manage college events |
| 📊 Dashboard | Live stats, charts, and overview |

---

## 🗂️ Project Structure

```
CollegeManagementSystem/
│
├── app.py                # Flask web app (auth + all modules)
├── database.py           # MySQL / PostgreSQL connection handler
├── config.py             # Loads settings from .env
├── mysql_setup.sql       # Run once to create all MySQL tables
├── .env                  # Your local environment variables (not on GitHub)
├── .env.example          # Template for .env
├── .gitignore            # Files excluded from Git
├── Procfile              # Render start command
├── requirements.txt      # Python packages
└── README.md             # This file
```

---

## ⚙️ Environment Variables

Create a `.env` file in the project root:

```env
# Application
PORT=8080
SECRET_KEY=college-management-secret-key-2026

# Set to true when using local MySQL
USE_MYSQL=true

# Supabase / Render PostgreSQL (used when USE_MYSQL=false)
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT.supabase.co:5432/postgres
```

---

## 🚀 Local Setup (MySQL)

### Prerequisites
- Python 3.11+
- MySQL 8.0+
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/Ayushpawar001/College_Mangement_System.git
cd College_Mangement_System
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create MySQL Database and Tables

Open MySQL and run:

```bash
mysql -u root -p < mysql_setup.sql
```

Or open **MySQL Workbench** → run `mysql_setup.sql`

### 5. Configure .env

```bash
copy .env.example .env    # Windows
```

Edit `.env` — set your MySQL password and `USE_MYSQL=true`

### 6. Run the App

```bash
python app.py
```

Open browser: **http://127.0.0.1:8080**

Login with:
- **Username:** `admin`
- **Password:** `Admin@2026`

---

## 🗄️ MySQL Database Schema

```sql
users       (user_id, username, email, password, role, created_at)
students    (student_id, user_id, name, age, gender, course, year, phone, email, address)
teachers    (teacher_id, user_id, name, subject, phone, email)
courses     (course_id, user_id, course_name, duration, fees)
attendance  (attendance_id, user_id, student_id, attendance_date, status)
marks       (mark_id, user_id, student_id, subject, marks)
fees        (fee_id, user_id, student_id, amount, payment_date, status)
events      (event_id, user_id, title, event_date, description)
```

Each table has a `user_id` column — data is isolated per logged-in account.

---

## 🌐 Deployment on Render

### Step 1 — Push code to GitHub

```bash
git add .
git commit -m "update"
git push origin main
```

### Step 2 — Create Web Service on Render

1. Go to **https://dashboard.render.com**
2. Click **+ New** → **Web Service**
3. Connect your GitHub repo
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`

### Step 3 — Add Environment Variables on Render

| Key | Value |
|---|---|
| `DATABASE_URL` | Your Render PostgreSQL internal URL |
| `SECRET_KEY` | `college-management-secret-key-2026` |
| `USE_MYSQL` | `false` |

### Step 4 — Create Render PostgreSQL Database

1. Click **+ New** → **PostgreSQL** → Free plan → Create
2. Copy the **Internal Database URL**
3. Paste it as `DATABASE_URL` in your web service environment

---

## 📦 Dependencies

```
Flask==3.0.3             # Web framework
gunicorn==22.0.0         # Production server (Render)
mysql-connector-python   # MySQL driver (local)
pg8000==1.31.2           # PostgreSQL driver (Render)
cryptography==42.0.8     # Password hashing support
```

---

## 🔐 Default Login

| Field | Value |
|---|---|
| Username | `admin` |
| Password | `Admin@2026` |

---

## 👤 Author

**Ayush Pawar**
- GitHub: [@Ayushpawar001](https://github.com/Ayushpawar001)
- Live Site: [https://college-mangement-system-6.onrender.com](https://college-mangement-system-6.onrender.com)
- Repo: [College Management System](https://github.com/Ayushpawar001/College_Mangement_System)

---

## 📄 License

For educational purposes at **PRMCEAM College**.
