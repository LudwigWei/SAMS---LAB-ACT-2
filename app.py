from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = "secret_key"

# Database Configuration (SQLite)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "users.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# QR Code Storage
QR_FOLDER = os.path.join(BASE_DIR, "static/qrcodes")
os.makedirs(QR_FOLDER, exist_ok=True)

# Store active QR codes (for expiration handling)
active_qr_codes = {}

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  # Hashed password
    role = db.Column(db.String(20), nullable=False)  # "Student" or "Professor"

# Class Model
class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(100), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    class_code = db.Column(db.String(10), unique=True, nullable=False)
    professor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Attendance Model
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    class_code = db.Column(db.String(20), nullable=False)
    checked_in = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        full_name = request.form["full_name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("User already exists. Try logging in.", "error")
            return redirect(url_for("login"))

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        new_user = User(full_name=full_name, email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("home"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session["user"] = user.email
            session["role"] = user.role

            flash("Login successful!", "success")

            if user.role == "Professor":
                return redirect(url_for("professor_dashboard"))
            elif user.role == "Student":
                return redirect(url_for("student_dashboard"))
        else:
            flash("Invalid credentials. Try again.", "error")

    return render_template("index.html")

@app.route("/studentDashboard")
def student_dashboard():
    if "user" not in session or session["role"] != "Student":
        return redirect(url_for("login"))
    return render_template("studentDashboard.html")

@app.route("/professorDashboard")
def professor_dashboard():
    if "user" not in session or session["role"] != "Professor":
        return redirect(url_for("login"))
    return render_template("professorDashboard.html")

@app.route("/professor/generate-qr/<class_code>")
def generate_qr(class_code):
    """Generates a QR code with an expiry time."""
    if "user" not in session or session["role"] != "Professor":
        return jsonify({"error": "Unauthorized"}), 403

    expiry_time = datetime.now() + timedelta(minutes=5)
    active_qr_codes[class_code] = expiry_time

    qr_url = f"http://yourwebsite.com/scan-qr/{class_code}"
    return jsonify({"qr_code": qr_url})

@app.route("/scan-qr/<class_code>", methods=["POST"])
def scan_qr(class_code):
    """Marks attendance for a student."""
    if class_code not in active_qr_codes or datetime.now() > active_qr_codes[class_code]:
        return jsonify({"error": "QR code has expired. Ask your professor for a new one."}), 403

    if "user" not in session or session["role"] != "Student":
        return jsonify({"error": "Unauthorized"}), 403

    user_email = session["user"]
    student = User.query.filter_by(email=user_email).first()

    if not student:
        return jsonify({"error": "Student not found."}), 404

    attendance = Attendance.query.filter_by(student_id=student.id, class_code=class_code).first()
    if not attendance:
        attendance = Attendance(student_id=student.id, class_code=class_code, checked_in=True)
        db.session.add(attendance)
    else:
        attendance.checked_in = True

    db.session.commit()
    return jsonify({"message": "Attendance marked successfully!"}), 200

@app.route("/professor/attendance/<class_code>")
def get_attendance(class_code):
    if "user" not in session or session["role"] != "Professor":
        return jsonify({"error": "Unauthorized"}), 403

    attendance_records = db.session.query(User.full_name, Attendance.checked_in)\
        .join(Attendance, User.id == Attendance.student_id)\
        .filter(Attendance.class_code == class_code).all()

    return jsonify([{"name": record[0], "checked": record[1]} for record in attendance_records])

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
