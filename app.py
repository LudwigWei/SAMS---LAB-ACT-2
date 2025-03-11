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

@app.route("/student_dashboard")
def student_dashboard():
    if "user" not in session or session["role"] != "Student":
        return jsonify({"error": "Unauthorized access."}), 403
    return jsonify({"message": "Welcome Student", "action": "Scan QR Code for Attendance"})

@app.route("/professor_dashboard")
def professor_dashboard():
    if "user" not in session or session["role"] != "Professor":
        return jsonify({"error": "Unauthorized access."}), 403
    return jsonify({"message": "Welcome Professor", "action": "View Student Attendance"})

# Route to generate a QR Code
@app.route("/professor/generate-qr/<classCode>", methods=["GET"])
def get_qr_code(classCode):
    qr_path = os.path.join(QR_FOLDER, f"{classCode}.png")

    # Generate QR Code if it doesn't exist
    if not os.path.exists(qr_path):
        qr = qrcode.make(f"http://127.0.0.1:5000/join/{classCode}")
        qr.save(qr_path)

    # Return the correct URL for the QR code
    return jsonify({"qr_code": url_for('serve_qr', filename=f"{classCode}.png", _external=True)}), 200

# Serve QR Code Images
@app.route("/static/qr_codes/<filename>")
def serve_qr(filename):
    return send_from_directory(QR_FOLDER, filename)

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "You have been logged out."}), 200

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
