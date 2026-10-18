USE college_db;

CREATE TABLE IF NOT EXISTS users (
    user_id    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    username   VARCHAR(100) UNIQUE NOT NULL,
    email      VARCHAR(150) UNIQUE NOT NULL,
    password   VARCHAR(256) NOT NULL,
    role       VARCHAR(20) DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS students (
    student_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id    INT UNSIGNED,
    name       VARCHAR(100) NOT NULL,
    age        INT,
    gender     VARCHAR(20),
    course     VARCHAR(100),
    year       INT,
    phone      VARCHAR(15),
    email      VARCHAR(100),
    address    VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS teachers (
    teacher_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id    INT UNSIGNED,
    name       VARCHAR(100) NOT NULL,
    subject    VARCHAR(100),
    phone      VARCHAR(15),
    email      VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS courses (
    course_id   INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id     INT UNSIGNED,
    course_name VARCHAR(100),
    duration    INT,
    fees        DECIMAL(10,2),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id       INT UNSIGNED,
    student_id    INT UNSIGNED,
    attendance_date DATE,
    status        VARCHAR(20),
    FOREIGN KEY (user_id)   REFERENCES users(user_id)       ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS marks (
    mark_id    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id    INT UNSIGNED,
    student_id INT UNSIGNED,
    subject    VARCHAR(100),
    marks      DECIMAL(5,2),
    FOREIGN KEY (user_id)   REFERENCES users(user_id)       ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS fees (
    fee_id       INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id      INT UNSIGNED,
    student_id   INT UNSIGNED,
    amount       DECIMAL(10,2),
    payment_date DATE,
    status       VARCHAR(20),
    FOREIGN KEY (user_id)   REFERENCES users(user_id)       ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS events (
    event_id    INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id     INT UNSIGNED,
    title       VARCHAR(100) NOT NULL,
    event_date  DATE NOT NULL,
    description VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Default admin user (password: Admin@2026)
INSERT IGNORE INTO users (username, email, password, role)
VALUES ('admin', 'admin@prmceam.com', 'a36aef5a11c4073fbe60314fc9df530a9d5f986533594d1f5190742ff9e0e408', 'admin');

SELECT CONCAT('Tables created: ', COUNT(*)) FROM information_schema.tables WHERE table_schema = 'college_db';
