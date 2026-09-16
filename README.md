# 🎓 PRMCEAM - College Management System

A full-featured College Management System built with **Python**, **Flask** (web) and **Tkinter** (desktop), connected to a **MySQL** database.

---

## 📋 Features

| Module | Description |
|---|---|
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
├── app.py                  # Flask web application
├── main.py                 # Tkinter desktop application
├── database.py             # MySQL database connection & queries
├── config.py               # Configuration loaded from .env
├── .env                    # Environment variables (not pushed to GitHub)
├── .env.example            # Sample environment variables
├── .gitignore              # Files ignored by Git
├── Procfile                # Render deployment config
├── requirements.txt        # Python dependencies
├── college_db SQL.sql      # Database schema (tables only)
├── college_db_backup.sql   # Full database backup (tables + data)
└── README.md               # Project documentation
```

---

## ⚙️ Environment Variables

Create a `.env` file in the root folder with these values:

```env
# Application
PORT=5000
SECRET_KEY=your-secret-key-here

# Database
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your-mysql-password
DB_NAME=college_db

# SSL - set true for cloud deployment (Render, Railway, etc.)
DB_SSL=false
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.10+
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

### 4. Setup Database

Open MySQL and run:

```bash
mysql -u root -p < "college_db SQL.sql"
```

Or open MySQL Workbench and import `college_db SQL.sql`.

### 5. Configure Environment

Copy `.env.example` to `.env` and fill in your values:

```bash
copy .env.example .env       # Windows
cp .env.example .env         # Mac/Linux
```

Edit `.env` with your MySQL credentials.

### 6. Run the Web App

```bash
python app.py
```

Open browser: **http://127.0.0.1:5000**

### 7. Run the Desktop App

```bash
python main.py
```

---

## 🗄️ Database Schema

```sql
students    (student_id, name, age, gender, course, year, phone, email, address)
teachers    (teacher_id, name, subject, phone, email)
courses     (course_id, course_name, duration, fees)
attendance  (attendance_id, student_id, attendance_date, status)
marks       (mark_id, student_id, subject, marks)
fees        (fee_id, student_id, amount, payment_date, status)
events      (event_id, title, event_date, description)
```

---

## 🌐 Deployment on Render

1. Push code to GitHub
2. Go to [https://dashboard.render.com](https://dashboard.render.com)
3. Create new **Web Service** → connect GitHub repo
4. Set **Build Command:** `pip install -r requirements.txt`
5. Set **Start Command:** `gunicorn app:app`
6. Add these **Environment Variables** in Render dashboard:

```
DB_HOST       = your-cloud-mysql-host
DB_PORT       = your-cloud-mysql-port
DB_USER       = your-cloud-mysql-user
DB_PASSWORD   = your-cloud-mysql-password
DB_NAME       = your-cloud-mysql-dbname
DB_SSL        = true
SECRET_KEY    = your-secret-key
PORT          = 5000
```

---

## 📦 Dependencies

```
mysql-connector-python   # MySQL database connector
Flask                    # Web framework
gunicorn                 # Production WSGI server
Pillow                   # Image processing (desktop app)
cryptography             # Encryption support
```

Install all with:
```bash
pip install -r requirements.txt
```

---

## 👤 Author

**Ayush Pawar**
- GitHub: [@Ayushpawar001](https://github.com/Ayushpawar001)
- Project: [College Management System](https://github.com/Ayushpawar001/College_Mangement_System)

---

## 📄 License

This project is for educational purposes at **PRMCEAM College**.
