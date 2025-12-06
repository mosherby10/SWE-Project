import os
import random
import string
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from models import db, User, Game, PasswordResetToken


app = Flask(__name__)

# === CONFIG ===
app.config["SECRET_KEY"] = "change-me"  # put a better secret later
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///store.db"  # use shared DB
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Uploads configuration for game images
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db.init_app(app)


# ========== ADMIN AUTH (DEMO) ========== #

def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            flash("You must be logged in as admin.", "danger")
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/admin_login")
def admin_login():
    # demo-only: treat this as admin login
    session["is_admin"] = True
    flash("Admin logged in (demo).", "success")
    return redirect(url_for("admin_games"))


@app.route("/admin_logout")
def admin_logout():
    session.pop("is_admin", None)
    flash("Admin logged out.", "info")
    return redirect(url_for("admin_games"))


# ========== BASIC USER AUTH (SIMPLE) ========== #

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))

        session["user_id"] = user.id
        flash("Logged in successfully.", "success")
        return redirect(url_for("index"))

    # GET
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))

        existing = User.query.filter_by(email=email).first()
        if existing:
            flash("Email already registered.", "warning")
            return redirect(url_for("register"))

        hashed = generate_password_hash(password)
        user = User(username=username, email=email, password=hashed)
        db.session.add(user)
        db.session.commit()

        flash("Account created. You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out.", "info")
    return redirect(url_for("login"))


@app.route("/")
def index():
    # for now, just redirect somewhere valid
    return redirect(url_for("admin_games"))


# ========== ADMIN GAME CRUD (WITH IMAGE) ========== #

@app.route("/admin/games")
@admin_required
def admin_games():
    games = Game.query.order_by(Game.id.desc()).all()
    return render_template("admin/games.html", games=games)


@app.route("/admin/games/create", methods=["GET", "POST"])
@admin_required
def admin_create_game():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        price_raw = request.form.get("price", "").strip()
        image_file = request.files.get("image")

        if not title:
            flash("Title is required.", "danger")
            return redirect(url_for("admin_create_game"))

        try:
            price = float(price_raw)
        except ValueError:
            flash("Invalid price.", "danger")
            return redirect(url_for("admin_create_game"))

        image_filename = None
        if image_file and image_file.filename:
            safe_name = secure_filename(image_file.filename)
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
            image_file.save(image_path)
            image_filename = safe_name

        game = Game(title=title, price=price, image_filename=image_filename)
        db.session.add(game)
        db.session.commit()
        flash("Game created.", "success")
        return redirect(url_for("admin_games"))

    return render_template("admin/game_form.html", mode="create", game=None)


@app.route("/admin/games/<int:game_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_game(game_id):
    game = Game.query.get_or_404(game_id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        price_raw = request.form.get("price", "").strip()
        image_file = request.files.get("image")

        if not title:
            flash("Title is required.", "danger")
            return redirect(url_for("admin_edit_game", game_id=game.id))

        try:
            price = float(price_raw)
        except ValueError:
            flash("Invalid price.", "danger")
            return redirect(url_for("admin_edit_game", game_id=game.id))

        game.title = title
        game.price = price

        if image_file and image_file.filename:
            safe_name = secure_filename(image_file.filename)
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
            image_file.save(image_path)
            game.image_filename = safe_name

        db.session.commit()
        flash("Game updated.", "success")
        return redirect(url_for("admin_games"))

    return render_template("admin/game_form.html", mode="edit", game=game)


@app.route("/admin/games/<int:game_id>/delete", methods=["POST"])
@admin_required
def admin_delete_game(game_id):
    game = Game.query.get_or_404(game_id)
    db.session.delete(game)
    db.session.commit()
    flash("Game deleted.", "info")
    return redirect(url_for("admin_games"))


# ========== PASSWORD RESET (OPTION A – CODE IN TERMINAL) ========== #

def generate_reset_code(length=6):
    # 6-digit numeric code
    return "".join(random.choices(string.digits, k=length))


@app.route("/password-reset/request", methods=["GET", "POST"])
def password_reset_request():
    if request.method == "POST":
        email = request.form.get("email", "").strip()

        user = User.query.filter_by(email=email).first()
        # Even if no user, show same message (to avoid leaking who exists)
        if not user:
            flash(
                "If that email exists in our system, a reset code has been generated.",
                "info",
            )
            return redirect(url_for("password_reset_verify"))

        # Create token
        code = generate_reset_code()
        expires_at = datetime.utcnow() + timedelta(minutes=10)

        token = PasswordResetToken(
            user_id=user.id,
            code=code,
            expires_at=expires_at,
        )
        db.session.add(token)
        db.session.commit()

        # OPTION A: print code in terminal (and container logs)
        print(f"[PASSWORD RESET] Code for {user.email} is: {code}")

        # Store email in session to know which account is being reset
        session["reset_email"] = user.email

        flash(
            "A reset code has been generated. Please check the console/logs (for demo) and enter it.",
            "success",
        )
        return redirect(url_for("password_reset_verify"))

    return render_template("password_reset_request.html")


@app.route("/password-reset/verify", methods=["GET", "POST"])
def password_reset_verify():
    email = session.get("reset_email")

    if not email:
        flash("Start by requesting a password reset.", "warning")
        return redirect(url_for("password_reset_request"))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("Something went wrong. Try again.", "danger")
        return redirect(url_for("password_reset_request"))

    if request.method == "POST":
        code_entered = request.form.get("code", "").strip()

        # Get latest valid token for this user
        token = (
            PasswordResetToken.query
            .filter_by(user_id=user.id, code=code_entered, used=False)
            .order_by(PasswordResetToken.created_at.desc())
            .first()
        )

        if (
            not token
            or token.expires_at < datetime.utcnow()
        ):
            flash("Invalid or expired code.", "danger")
            return redirect(url_for("password_reset_verify"))

        # Mark as verified in session
        session["reset_verified"] = True
        flash("Code verified. You can now set a new password.", "success")
        return redirect(url_for("password_reset_new"))

    return render_template("password_reset_verify.html", email=email)


@app.route("/password-reset/new", methods=["GET", "POST"])
def password_reset_new():
    email = session.get("reset_email")
    verified = session.get("reset_verified")

    if not email or not verified:
        flash("You must verify a reset code first.", "warning")
        return redirect(url_for("password_reset_request"))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("Something went wrong. Try again.", "danger")
        return redirect(url_for("password_reset_request"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not password:
            flash("Password cannot be empty.", "danger")
            return redirect(url_for("password_reset_new"))

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("password_reset_new"))

        # Update user password (hashed)
        user.password = generate_password_hash(password)
        # Mark all tokens for that user as used
        PasswordResetToken.query.filter_by(user_id=user.id, used=False).update(
            {"used": True}
        )

        db.session.commit()

        # Clear reset session
        session.pop("reset_email", None)
        session.pop("reset_verified", None)

        flash("Your password has been reset. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("password_reset_form.html", email=email)


# ========== RUN ========== #

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    # If you use Docker, keep host="0.0.0.0"
    app.run(host="0.0.0.0", port=5000, debug=True)
