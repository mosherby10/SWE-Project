from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)  # Secret key for sessions
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    # Check if user is logged in
    user_logged_in = 'user_id' in session
    username = session.get('username', '')
    return render_template("index.html", user_logged_in=user_logged_in, username=username)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if user exists
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            # Login successful
            session['user_id'] = user.id
            session['username'] = user.username
            session['email'] = user.email
            flash('Login successful!', 'success')
            return redirect(url_for("home"))
        else:
            # Invalid credentials
            flash('Invalid email or password. Please try again.', 'error')
            return render_template("login.html")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validation
        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template("register.html")

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template("register.html")

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please login instead.', 'error')
            return render_template("register.html")

        # Check if username already exists
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash('Username already taken. Please choose another.', 'error')
            return render_template("register.html")

        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for("login"))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')
            return render_template("register.html")

    return render_template("register.html")

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get('email')

        # Check if email exists in database
        user = User.query.filter_by(email=email).first()

        if user:
            # Here you would typically:
            # 1. Generate a reset token
            # 2. Send email with reset link
            # 3. Store token in database with expiration
            print(f"Password reset requested for: {email}")
            flash('If an account exists with this email, a password reset link has been sent.', 'success')
            return render_template("forgot_password.html", success=True)
        else:
            # Don't reveal if email exists for security
            flash('If an account exists with this email, a password reset link has been sent.', 'success')
            return render_template("forgot_password.html", success=True)

    return render_template("forgot_password.html")

@app.route("/logout")
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)

