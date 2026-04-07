import sqlite3

conn = sqlite3.connect("career_guidance.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM career_predictions")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()