from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# Track active users
active_users = set()

# Store logs
user_logs = []


# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user"] = username
            session["role"] = user[3]  # role column

            active_users.add(username)

            # log login
            user_logs.append({
                "user": username,
                "action": "Login",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M")
            })

            if user[3] == "admin":
                return redirect("/")
            else:
                return redirect("/user_dashboard")

        return "Invalid credentials"

    return render_template("login.html")


# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, 'user')",
            (username, password)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


# ---------- DASHBOARD (ADMIN ONLY) ----------
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return redirect("/user_dashboard")

    return render_template("index.html")


# ---------- DASHBOARD DATA ----------
@app.route("/dashboard_data")
def dashboard_data():
    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"})

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    conn.close()

    active_count = len(active_users)

    # count only threat logs
    threat_actions = ["Financial File Access", "Database Access", "Upload File"]
    threats = [log for log in user_logs if log["action"] in threat_actions]

    return jsonify({
        "total_users": total_users,
        "active_sessions": active_count,
        "threat_count": len(threats)
    })


# ---------- GET USERS ----------
@app.route("/get_users")
def get_users():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"})

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM users")
    users = cursor.fetchall()
    conn.close()

    return jsonify([{"username": u[0]} for u in users])


# ---------- USER DASHBOARD ----------
@app.route("/user_dashboard")
def user_dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("user_dashboard.html")


# ---------- LOG USER ACTION ----------
@app.route("/log_action", methods=["POST"])
def log_action():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"})

    data = request.get_json()
    action = data.get("action")

    log = {
        "user": session["user"],
        "action": action,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M")
    }

    user_logs.append(log)

    return jsonify({"message": "Action Logged"})


# ---------- DETECT THREATS (ADMIN ONLY) ----------
@app.route("/detect")
def detect():
    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"})

    threat_actions = ["Financial File Access", "Database Access", "Upload File"]

    threats = [log for log in user_logs if log["action"] in threat_actions]

    return jsonify(threats)


# ---------- ACTIVITY ----------
@app.route("/get_activity")
def get_activity():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"})

    return jsonify(user_logs)


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    user = session.get("user")

    if user in active_users:
        active_users.remove(user)

    # log logout
    user_logs.append({
        "user": user,
        "action": "Logout",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M")
    })

    session.clear()
    return redirect("/login")

@app.route("/activity")
def activity():
    if "user" not in session:
        return redirect("/login")
    return render_template("activity.html")

@app.route("/alerts")
def alerts():
    if "user" not in session:
        return redirect("/login")
    return render_template("alerts.html")


# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)