from flask import Flask, render_template, request, session, redirect, url_for, jsonify
import pickle
import numpy as np
import sqlite3
import requests
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "career_guidance_secret_key"

# Helper function to get database connection
def get_db_connection():
    conn = sqlite3.connect("career_guidance.db")
    conn.row_factory = sqlite3.Row
    return conn

# Load model and encoders
# ... (rest of the code below)
model = pickle.load(open("career_model.pkl", "rb"))
interest_encoder = pickle.load(open("interest_encoder.pkl", "rb"))
career_encoder = pickle.load(open("career_encoder.pkl", "rb"))

print("Interest classes:", interest_encoder.classes_)

career_roadmaps = {
    "Software Developer": [
        "Learn Python, Java, or C++",
        "Practice Data Structures and Algorithms",
        "Build real-world software projects",
        "Learn Git and GitHub",
        "Prepare for coding interviews"
    ],
    "Web Developer": [
        "Learn HTML, CSS, and JavaScript",
        "Practice responsive web design",
        "Learn frontend frameworks like React",
        "Learn backend development with Flask or Node.js",
        "Build portfolio websites and projects"
    ],
    "Data Scientist": [
        "Learn Python programming",
        "Study Pandas, NumPy, and Matplotlib",
        "Learn Machine Learning algorithms",
        "Practice SQL and data cleaning",
        "Build data analysis and prediction projects"
    ],
    "Database Administrator": [
        "Learn SQL deeply",
        "Understand database design and normalization",
        "Practice MySQL or PostgreSQL",
        "Learn backup and recovery methods",
        "Understand database security and optimization"
    ],
    "UI/UX Designer": [
        "Learn design principles and color theory",
        "Practice Figma or Adobe XD",
        "Study user experience fundamentals",
        "Create wireframes and prototypes",
        "Build a design portfolio"
    ],
    "Cybersecurity Analyst": [
        "Learn networking fundamentals",
        "Understand system security basics",
        "Study ethical hacking concepts",
        "Learn tools like Wireshark and Nmap",
        "Practice cybersecurity labs and challenges"
    ]
}


@app.route("/")
def home():
    interest_options = list(interest_encoder.classes_)
    return render_template("index.html", interest_options=interest_options)


@app.route("/predict", methods=["POST"])
def predict():
    student_name = request.form["student_name"]
    academic_percentage = int(request.form["academic_percentage"])
    python_skill = int(request.form["python_skill"])
    web_skill = int(request.form["web_skill"])
    database_skill = int(request.form["database_skill"])
    communication_skill = int(request.form["communication_skill"])
    problem_solving_skill = int(request.form["problem_solving_skill"])
    interest_area = request.form["interest_area"]
    logical_reasoning = int(request.form["logical_reasoning"])
    creativity = int(request.form["creativity"])

    interest_area_encoded = interest_encoder.transform([interest_area])[0]

    features = np.array([[
        academic_percentage,
        python_skill,
        web_skill,
        database_skill,
        communication_skill,
        problem_solving_skill,
        interest_area_encoded,
        logical_reasoning,
        creativity
    ]])

    probabilities = model.predict_proba(features)[0]
    top_3_indices = np.argsort(probabilities)[::-1][:3]

    recommendations = []
    for idx in top_3_indices:
        career_name = career_encoder.inverse_transform([idx])[0]
        confidence = round(probabilities[idx] * 100, 2)
        recommendations.append((career_name, confidence))

    top_career = recommendations[0][0]
    roadmap = career_roadmaps.get(top_career, [])

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO career_predictions (
            student_name,
            academic_percentage,
            python_skill,
            web_skill,
            database_skill,
            communication_skill,
            problem_solving_skill,
            interest_area,
            logical_reasoning,
            creativity,
            recommendation_1,
            recommendation_2,
            recommendation_3
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        student_name,
        academic_percentage,
        python_skill,
        web_skill,
        database_skill,
        communication_skill,
        problem_solving_skill,
        interest_area,
        logical_reasoning,
        creativity,
        recommendations[0][0],
        recommendations[1][0],
        recommendations[2][0]
    ))

    conn.commit()
    conn.close()

    return render_template("result.html", recommendations=recommendations, roadmap=roadmap)


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")

    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "llama3.2",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful AI career guidance assistant for students. Give short, simple, and useful answers."
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        "stream": False
    }

    try:
        response = requests.post(url, json=payload)
        data = response.json()
        reply = data["message"]["content"]
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"Chatbot error: {str(e)}"}), 500


@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        admin = conn.execute("SELECT * FROM admins WHERE username = ?", (username,)).fetchone()
        conn.close()

        if admin and check_password_hash(admin["password"], password):
            session["admin_logged_in"] = True
            session["admin_user"] = admin["username"]
            return redirect(url_for("admin"))
        else:
            error = "Invalid username or password"

    return render_template("admin_login.html", error=error)


@app.route("/admin/change_password", methods=["GET", "POST"])
def change_password():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    message = None
    if request.method == "POST":
        old_password = request.form["old_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if new_password != confirm_password:
            message = "New passwords do not match"
        else:
            conn = get_db_connection()
            admin = conn.execute("SELECT * FROM admins WHERE username = ?", (session["admin_user"],)).fetchone()

            if admin and check_password_hash(admin["password"], old_password):
                hashed_password = generate_password_hash(new_password)
                conn.execute("UPDATE admins SET password = ? WHERE username = ?", (hashed_password, session["admin_user"]))
                conn.commit()
                message = "Password updated successfully!"
            else:
                message = "Incorrect old password"
            conn.close()

    return render_template("change_password.html", message=message)


@app.route("/admin/forgot_password", methods=["GET", "POST"])
def forgot_password():
    step = 1
    error = None
    username = request.args.get("username") or request.form.get("username")
    question = None

    if username:
        conn = get_db_connection()
        admin = conn.execute("SELECT * FROM admins WHERE username = ?", (username,)).fetchone()
        conn.close()
        if admin:
            question = admin["security_question"]
            step = 2
        else:
            error = "Username not found"
            step = 1

    if request.method == "POST" and "answer" in request.form:
        answer = request.form["answer"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        conn = get_db_connection()
        admin = conn.execute("SELECT * FROM admins WHERE username = ?", (username,)).fetchone()

        if admin and check_password_hash(admin["security_answer"], answer):
            if new_password == confirm_password:
                hashed_password = generate_password_hash(new_password)
                conn.execute("UPDATE admins SET password = ? WHERE username = ?", (hashed_password, username))
                conn.commit()
                conn.close()
                return redirect(url_for("admin_login", message="Password reset successfully!"))
            else:
                error = "Passwords do not match"
        else:
            error = "Incorrect answer to security question"
        conn.close()
        step = 2

    return render_template("forgot_password.html", step=step, error=error, username=username, question=question)


@app.route("/admin")
def admin():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    conn = sqlite3.connect("career_guidance.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM career_predictions ORDER BY id DESC")
    records = cursor.fetchall()

    conn.close()

    return render_template("admin.html", records=records)


@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    app.run(debug=True)