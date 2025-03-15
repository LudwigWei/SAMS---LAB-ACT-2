from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import io
import base64
import qrcode
import os

app = Flask(__name__)
app.secret_key = "secret_key"

# Database Configuration (SQLite)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "users.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

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
    """Generates a QR code dynamically without saving a file."""
    if "user" not in session or session["role"] != "Professor":
        return jsonify({"error": "Unauthorized"}), 403

    expiry_time = datetime.now() + timedelta(minutes=5)
    active_qr_codes[class_code] = expiry_time

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5
    )
    qr.add_data(f"http://yourwebsite.com/scan-qr/{class_code}")
    qr.make(fit=True)

    # Convert to Base64
    img = qr.make_image(fill="black", back_color="white")
    img_io = io.BytesIO()
    img.save(img_io, format="PNG")
    img_io.seek(0)
    qr_base64 = base64.b64encode(img_io.getvalue()).decode("utf-8")

    return jsonify({"qr_code": f"data:image/png;base64,{qr_base64}"})

@app.route("/professor/create-class", methods=["POST"])
def create_class():
    """Allows professors to create a new class."""
    if "user" not in session or session["role"] != "Professor":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    class_name = data.get("class_name")
    section = data.get("section")
    class_code = data.get("class_code")

    if not class_name or not section or not class_code:
        return jsonify({"error": "All fields are required."}), 400

    existing_class = Class.query.filter_by(class_code=class_code).first()
    if existing_class:
        return jsonify({"error": "Class with this code already exists."}), 400

    professor = User.query.filter_by(email=session["user"]).first()
    if not professor:
        return jsonify({"error": "Professor not found."}), 404

    new_class = Class(class_name=class_name, section=section, class_code=class_code, professor_id=professor.id)

    try:
        db.session.add(new_class)
        db.session.commit()
        return jsonify({"success": True, "message": "Class created successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

@app.route("/professor/classes")
def get_classes():
    """Fetch all classes handled by the logged-in professor."""
    if "user" not in session or session["role"] != "Professor":
        return jsonify({"error": "Unauthorized"}), 403

    professor = User.query.filter_by(email=session["user"]).first()
    if not professor:
        return jsonify({"error": "Professor not found."}), 404

    classes = Class.query.filter_by(professor_id=professor.id).all()

    return jsonify({"classes": [
        {"class_name": c.class_name, "section": c.section, "class_code": c.class_code}
        for c in classes
    ]}), 200

@app.route("/professor/attendance-data/<class_code>")
def get_attendance(class_code):
    """Fetches attendance records for a specific class."""
    if "user" not in session or session["role"] != "Professor":
        return jsonify({"error": "Unauthorized"}), 403

    attendance_records = (
        db.session.query(User.full_name, Attendance.checked_in)
        .join(Attendance, User.id == Attendance.student_id, isouter=True)
        .filter(Attendance.class_code == class_code)
        .all()
    )

    attendance_list = [{"name": record[0], "checked": record[1] if record[1] is not None else False} for record in attendance_records]

    return jsonify(attendance_list), 200

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
