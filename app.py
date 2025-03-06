from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
app.secret_key = "secret_key"

# Database Configuration (SQLite)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "users.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

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

@app.route("/student_dashboard")
def student_dashboard():
    if "user" not in session or session["role"] != "Student":
        return redirect(url_for("login"))
    return render_template("studentDashboard.html")

@app.route("/professor_dashboard")
def professor_dashboard():
    if "user" not in session or session["role"] != "Professor":
        return redirect(url_for("login"))
    return render_template("professorDashboard.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
