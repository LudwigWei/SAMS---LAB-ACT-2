from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from qr_generator import generate_qr_code
import os

app = Flask(__name__)
app.secret_key = "secret_key"


# Database Configuration (SQLite)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "users.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

## For QR generation
QR_FOLDER = os.path.join(BASE_DIR, "static/qrcodes")
os.makedirs(QR_FOLDER, exist_ok=True)

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
    professor = db.relationship('User', backref=db.backref('classes', lazy=True))


# Create Database
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

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("User already exists. Try logging in.", "error")
            return redirect(url_for("login"))

        # Hash password before storing
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        # Add new user
        new_user = User(full_name=full_name, email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("home"))  # Redirect to the landing page

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

            # Redirect based on role
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
    """Generates a QR code for the given class code and returns its URL."""
    if "user" not in session or session["role"] != "Professor":
        return jsonify({"error": "Unauthorized"}), 403

    filename = generate_qr_code(class_code)
    qr_url = url_for("static", filename=f"qrcodes/{filename}", _external=True)

    return jsonify({"qr_code": qr_url})

@app.route("/professor/create-class", methods=["POST"])
def create_class():
    if "user" not in session or session["role"] != "Professor":
        return jsonify({"error": "Unauthorized"}), 403

    # Get class details from the form
    class_name = request.json.get("class_name")
    section = request.json.get("section")
    class_code = request.json.get("class_code")

    # Validate the data
    if not class_name or not section or not class_code:
        return jsonify({"error": "All fields are required."}), 400

    # Check if the class code already exists
    existing_class = Class.query.filter_by(class_code=class_code).first()
    if existing_class:
        return jsonify({"error": "Class with this code already exists."}), 400

    # Add new class to the database
    professor_id = User.query.filter_by(email=session["user"]).first().id
    new_class = Class(class_name=class_name, section=section, class_code=class_code, professor_id=professor_id)

    try:
        db.session.add(new_class)
        db.session.commit()
        return jsonify({"success": True, "message": "Class created successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error creating class: {str(e)}"}), 500


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
