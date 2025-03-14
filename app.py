from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
import qrcode

app = Flask(__name__)
app.secret_key = "secret_key"

# Database Configuration (SQLite)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "users.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

QR_FOLDER = "static/qr_codes"
os.makedirs(QR_FOLDER, exist_ok=True)  # Ensure QR code directory exists

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  # Hashed password
    role = db.Column(db.String(20), nullable=False)  # "Student" or "Professor"

# Attendance Model
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    class_code = db.Column(db.String(20), nullable=False)
    checked_in = db.Column(db.Boolean, default=False)

# Create Database
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    full_name = data.get("full_name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "User already exists. Try logging in."}), 400

    # Hash password before storing
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    # Add new user
    new_user = User(full_name=full_name, email=email, password=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Account created successfully! Please log in."}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password, password):
        session["user"] = user.email
        session["role"] = user.role

        return jsonify({"message": "Login successful!", "role": user.role}), 200
    else:
        return jsonify({"error": "Invalid credentials. Try again."}), 401

@app.route("/scan-qr/<classCode>", methods=["POST"])
def scan_qr(classCode):
    if "user" not in session or session["role"] != "Student":
        return jsonify({"error": "Unauthorized access."}), 403

    user_email = session["user"]
    student = User.query.filter_by(email=user_email).first()

    if not student:
        return jsonify({"error": "Student not found."}), 404

    attendance = Attendance.query.filter_by(student_id=student.id, class_code=classCode).first()

    if attendance:
        attendance.checked_in = True
    else:
        attendance = Attendance(student_id=student.id, class_code=classCode, checked_in=True)
        db.session.add(attendance)

    db.session.commit()
    return jsonify({"message": "Attendance marked successfully."}), 200

@app.route("/professor/attendance/<classCode>", methods=["GET"])
def get_attendance(classCode):
    if "user" not in session or session["role"] != "Professor":
        return jsonify({"error": "Unauthorized access."}), 403

    attendance_records = (
        db.session.query(User.full_name, Attendance.checked_in)
        .join(Attendance, User.id == Attendance.student_id)
        .filter(Attendance.class_code == classCode)
        .all()
    )

    attendance_list = [
        {"name": record[0], "checked": record[1]} for record in attendance_records
    ]

    return jsonify(attendance_list), 200

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "You have been logged out."}), 200

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
