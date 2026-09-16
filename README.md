# 🎓 PRMCEAM - College Management System

A full-featured College Management System built with **Python** and **Flask**, connected to **Supabase PostgreSQL** database with full authentication.

---

## 📋 Features

| Module | Description |
|---|---|
| 🔐 Authentication | Login / Register / Logout system |
| 🎓 Students | Add, update, delete, view student records |
| 👨‍🏫 Teachers | Manage teacher information |
| 📚 Courses | Manage course details and fees |
| ✅ Attendance | Mark and track student attendance |
| 📝 Marks | Record and view student marks |
| 💰 Fees | Track fee payments and status |
| 📅 Events | Add and manage college events |
| 📊 Dashboard | Live stats and overview of all modules |

---

## 🗂️ Project Structure

```
CollegeManagementSystem/
│
├── app.py                    # Flask web application (with auth)
├── database.py               # PostgreSQL connection (Supabase)
├── config.py                 # Configuration loaded from .env
├── setup_db.py               # Run once to create tables on Supabase
├── create_users_table.py     # Run once to create users table
├── .env                      # Environment variables (not pushed to GitHub)
├── .env.example              # Sample environment variables
├── .gitignore                # Files ignored by Git
├── Procfile                  # Render deployment config
├── runtime.txt               # Python version for Render
├── .python-version           # Python version pin
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## ⚙️ Environment Variables

Create a `.env` file in the root folder:

```env
# Application
PORT=5000
SECRET_KEY=your-secret-key-here

# Supabase PostgreSQL
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.YOUR_PROJECT.supabase.co:5432/postgres
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.11+
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

### 4. Configure Environment

```bash
copy .env.example .env       # Windows
cp .env.example .env         # Mac/Linux
```

Edit `.env` with your Supabase credentials.

### 5. Setup Database Tables

```bash
python setup_db.py
python create_users_table.py
```

### 6. Run the Web App

```bash
python app.py
```

Open browser: **http://127.0.0.1:5000**

Login with:
- **Username:** `admin`
- **Password:** `Admin@2026`

---

## 🗄️ Database Schema

```
students    (student_id, name, age, gender, course, year, phone, email, address)
teachers    (teacher_id, name, subject, phone, email)
courses     (course_id, course_name, duration, fees)
attendance  (attendance_id, student_id, attendance_date, status)
marks       (mark_id, student_id, subject, marks)
fees        (fee_id, student_id, amount, payment_date, status)
events      (event_id, title, event_date, description)
users       (user_id, username, email, password, role, created_at)
```

---

## 🌐 Deployment on Render

1. Push code to GitHub
2. Go to **https://dashboard.render.com**
3. Create new **Web Service** → connect GitHub repo
4. Set **Build Command:** `pip install -r requirements.txt`
5. Set **Start Command:** `gunicorn app:app`
6. Add **Environment Variables:**

| Key | Value |
|---|---|
| `PYTHON_VERSION` | `3.11.9` |
| `DATABASE_URL` | your Supabase connection string |
| `SECRET_KEY` | your secret key |
| `PORT` | `5000` |

---

## 📦 Dependencies

```
Flask==3.0.3          # Web framework
gunicorn==22.0.0      # Production WSGI server
psycopg2-binary       # PostgreSQL driver
cryptography==42.0.8  # Encryption support
```

---

## 👤 Author

**Ayush Pawar**
- GitHub: [@Ayushpawar001](https://github.com/Ayushpawar001)
- Project: [College Management System](https://github.com/Ayushpawar001/College_Mangement_System)

---

## 📄 License

This project is for educational purposes at **PRMCEAM College**.
