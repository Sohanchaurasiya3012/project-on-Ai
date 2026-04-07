import sqlite3

# Connect to database (it will create the file if it does not exist)
conn = sqlite3.connect("career_guidance.db")
cursor = conn.cursor()

# Create table for career predictions
cursor.execute("""
CREATE TABLE IF NOT EXISTS career_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    academic_percentage INTEGER,
    python_skill INTEGER,
    web_skill INTEGER,
    database_skill INTEGER,
    communication_skill INTEGER,
    problem_solving_skill INTEGER,
    interest_area TEXT,
    logical_reasoning INTEGER,
    creativity INTEGER,
    recommendation_1 TEXT,
    recommendation_2 TEXT,
    recommendation_3 TEXT
)
""")

# Create table for admin credentials
cursor.execute("""
CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    security_question TEXT,
    security_answer TEXT
)
""")

# Insert default admin if not exists
from werkzeug.security import generate_password_hash
default_username = "admin"
default_password = generate_password_hash("Sohan@2026")
default_question = "What is your favorite color?"
default_answer = generate_password_hash("Blue")

cursor.execute("SELECT * FROM admins WHERE username = ?", (default_username,))
if not cursor.fetchone():
    cursor.execute("""
        INSERT INTO admins (username, password, security_question, security_answer)
        VALUES (?, ?, ?, ?)
    """, (default_username, default_password, default_question, default_answer))

conn.commit()
conn.close()

print("Database and table created successfully.")