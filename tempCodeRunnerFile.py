from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Game, Order, OrderItem, Admin, PasswordResetToken, Review, ActivityLog, Notification
from decimal import Decimal
from datetime import datetime, timedelta
import random
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gaming_store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads/profiles'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db.init_app(app)

# ================= DATABASE INIT =================
with app.app_context():
    db.create_all()

    # Add games if not existing
    if not Game.query.first():
        games = [
            Game(title="PubG", category="Battle Royale", price=Decimal("24.99"), rating=4.7, downloads=2200000, image="assets/images/Pubg.jfif"),
            Game(title="Call of Duty", category="Shooter", price=Decimal("49.99"), rating=4.8, downloads=2500000, image="assets/images/call_of_duty.jfif"),
            Game(title="Roblox", category="Sandbox", price=Decimal("19.99"), rating=4.5, downloads=3000000, image="assets/images/Roblox.jfif"),
            Game(title="Minecraft", category="Sandbox", price=Decimal("29.99"), rating=4.9, downloads=3500000, image="assets/images/Miencraft.jfif"),
            Game(title="eFootball", category="Sports", price=Decimal("39.99"), rating=4.6, downloads=1800000, image="assets/images/efootball.jfif"),
            Game(title="Fortnite", category="Battle Royale", price=Decimal("0.00"), rating=4.8, downloads=2300000, image="assets/images/Fortnite.jpg"),
            Game(title="FC26", category="Sports", price=Decimal("34.99"), rating=4.4, downloads=1500000, image="assets/images/FC26.jfif"),
            Game(title="FC25", category="Sports", price=Decimal("29.99"), rating=4.3, downloads=1200000, image="assets/images/FC25.jfif"),
        ]
        db.session.add_all(games)
        db.session.commit()

    # Add default admin if not existing
    if not Admin.query.first():
        default_admin = Admin(
            name="Admin",
            email="admin@admin.com",
            password=generate_password_hash("admin123")
        )
        db.session.add(default_admin)
        db.session.commit()


# ================= CART SESSION INIT =================
def init_cart():
    if "cart" not in session:
        session["cart"] = {}


# ================= HOME PAGE =================
@app.route("/")
def home():
    user_logged_in = 'user_id' in session
    username = session.get('username', '')
    user = None
    if session.get('user_id'):
        user = User.query.get(session['user_id'])
    return render_template("index.html", user_logged_in=user_logged_in, username=username, user=user)


# ================= AUTH =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Check if admin login (@admin.com)
        if email.endswith("@admin.com"):
            admin = Admin.query.filter_by(email=email).first()
            if admin and check_password_hash(admin.password, password):
                session["admin_id"] = admin.id
                session["admin_name"] = admin.name
                session["is_admin"] = True
                flash("Admin login successful!", "success")
                return redirect(url_for("admin_dashboard"))
            flash("Invalid admin credentials!", "error")
            return render_template("login.html")

        # Regular user login
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            session["is_admin"] = False
            
            # Create welcome notification
            welcome_notification = Notification(
                user_id=user.id,
                message=f"Welcome back, {user.username}! We're glad to have you here.",
                is_read=False
            )
            db.session.add(welcome_notification)
            db.session.commit()
            
            flash("Login successful!", "success")
            return redirect(url_for("home"))

        flash("Invalid credentials!", "error")
        return render_template("login.html")

    return render_template("login.html")
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return render_template("register.html")

        # Check if trying to register as admin
        if email.endswith("@admin.com"):
            # Check if admin already exists
            if Admin.query.filter_by(email=email).first():
                flash("Admin email already registered!", "error")
                return render_template("register.html")
            
            # Create new admin
            hashed_password = generate_password_hash(password)
            new_admin = Admin(name=username, email=email, password=hashed_password)
            db.session.add(new_admin)
            db.session.commit()
            
            # Auto-login as admin
            session["admin_id"] = new_admin.id
            session["admin_name"] = new_admin.name
            session["is_admin"] = True
            flash("Admin account created successfully! Welcome to Admin Dashboard!", "success")
            return redirect(url_for("admin_dashboard"))
        
        # Regular user registration
        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "error")
            return render_template("register.html")

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password, balance=Decimal("100.00"))
        db.session.add(new_user)
        db.session.commit()

        # Auto-login after registration
        session["user_id"] = new_user.id
        session["username"] = new_user.username
        session["is_admin"] = False
        flash("Account created successfully! Welcome to Game-verse!", "success")
        return redirect(url_for("home"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for("home"))


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    flash("Admin logged out successfully!", "info")
    return redirect(url_for("home"))


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if not user:
            # Don't reveal if email exists for security
            flash("If account exists, a reset code has been sent!", "success")
            return render_template("password_reset_request.html")

        # Generate 6-digit code
        reset_code = str(random.randint(100000, 999999))
        
        # Set expiration (15 minutes)
        expires_at = datetime.utcnow() + timedelta(minutes=15)
        
        # Invalidate any existing tokens for this email
        PasswordResetToken.query.filter_by(email=email, used=False).update({"used": True})
        db.session.commit()
        
        # Create new token
        reset_token = PasswordResetToken(
            email=email,
            token=reset_code,
            expires_at=expires_at
        )
        db.session.add(reset_token)
        db.session.commit()

        # In production, send email here. For demo, print to console
        print(f"Password reset code for {email}: {reset_code}")
        
        flash("Reset code generated! Check console/logs for demo.", "success")
        return redirect(url_for("verify_reset_code", email=email))

    return render_template("password_reset_request.html")


@app.route("/verify-reset-code/<email>", methods=["GET", "POST"])
def verify_reset_code(email):
    if request.method == "POST":
        code = request.form.get('code')
        
        # Find valid token
        token = PasswordResetToken.query.filter_by(
            email=email,
            token=code,
            used=False
        ).first()
        
        if not token:
            flash("Invalid reset code!", "error")
            return render_template("password_reset_verify.html", email=email)
        
        if datetime.utcnow() > token.expires_at:
            flash("Reset code has expired! Please request a new one.", "error")
            token.used = True
            db.session.commit()
            return redirect(url_for("forgot_password"))
        
        # Don't mark as used yet - allow user to reset password
        # Token will be marked as used when password is actually reset
        # Redirect to reset password form with token
        return redirect(url_for("reset_password", email=email, token=code))
    
    return render_template("password_reset_verify.html", email=email)


@app.route("/reset-password/<email>", methods=["GET", "POST"])
def reset_password(email):
    token_code = request.args.get('token') or request.form.get('token')
    
    if request.method == "POST":
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return render_template("password_reset_form.html", email=email)
        
        # Verify token is valid and not used
        token = PasswordResetToken.query.filter_by(
            email=email,
            token=token_code,
            used=False
        ).first()
        
        if not token:
            flash("Invalid or already used reset token! Please request a new one.", "error")
            return redirect(url_for("forgot_password"))
        
        if datetime.utcnow() > token.expires_at:
            flash("Reset code has expired! Please request a new one.", "error")
            token.used = True
            db.session.commit()
            return redirect(url_for("forgot_password"))
        
        # Update user password
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(password)
            # Mark token as used
            token.used = True
            db.session.commit()
            flash("Password reset successful! Please login with your new password.", "success")
            return redirect(url_for("login"))
        else:
            flash("User not found!", "error")
            return redirect(url_for("forgot_password"))
    
    # GET request - verify token is valid
    if token_code:
        token = PasswordResetToken.query.filter_by(
            email=email,
            token=token_code
        ).first()
        
        if not token:
            flash("Invalid reset token!", "error")
            return redirect(url_for("forgot_password"))
        
        if datetime.utcnow() > token.expires_at:
            flash("Reset code has expired! Please request a new one.", "error")
            return redirect(url_for("forgot_password"))
    
    return render_template("password_reset_form.html", email=email)


# ================= BROWSE =================
@app.route("/browse")
def browse():
    query = request.args.get("q", "")
    games = Game.query.filter(Game.title.ilike(f"%{query}%")).all() if query else Game.query.all()
    user = None
    if session.get('user_id'):
        user = User.query.get(session['user_id'])
    return render_template("browse.html", games=games, user=user)


@app.route("/game/<int:game_id>")
def game_review(game_id):
    game = Game.query.get_or_404(game_id)
    all_reviews = Review.query.filter_by(game_id=game_id).order_by(Review.created_at.desc()).all()
    
    # Get current user's review if exists
    user_review = None
    other_reviews = []
    user = None
    if session.get('user_id'):
        user = User.query.get(session['user_id'])
        user_review = Review.query.filter_by(game_id=game_id, user_id=session['user_id']).first()
        # Filter out user's review from other reviews
        other_reviews = [r for r in all_reviews if r.user_id != session['user_id']]
    else:
        other_reviews = all_reviews
    
    return render_template("game_review.html", game=game, reviews=all_reviews, user_review=user_review, other_reviews=other_reviews, user=user)


@app.route("/game/<int:game_id>/add-review", methods=["POST"])
def add_review(game_id):
    if not session.get('user_id'):
        flash("Please login to add a review!", "error")
        return redirect(url_for("login"))
    
    comment = request.form.get('comment', '').strip()
    rating = request.form.get('rating')
    
    if not comment:
        flash("Comment cannot be empty!", "error")
        return redirect(url_for("game_review", game_id=game_id))
    
    # Check if user already has a review for this game
    existing_review = Review.query.filter_by(game_id=game_id, user_id=session['user_id']).first()
    if existing_review:
        flash("You already have a review for this game. You can edit it instead!", "error")
        return redirect(url_for("game_review", game_id=game_id))
    
    # Create new review
    new_review = Review(
        user_id=session['user_id'],
        game_id=game_id,
        comment=comment,
        rating=float(rating) if rating else None
    )
    
    db.session.add(new_review)
    
    # Create notification for review
    game = Game.query.get(game_id)
    notification = Notification(
        user_id=session['user_id'],
        message=f"You added a review for {game.title}",
        is_read=False
    )
    db.session.add(notification)
    db.session.commit()
    
    flash("Review added successfully!", "success")
    return redirect(url_for("game_review", game_id=game_id))


@app.route("/game/<int:game_id>/edit-review/<int:review_id>", methods=["POST"])
def edit_review(game_id, review_id):
    if not session.get('user_id'):
        flash("Please login to edit a review!", "error")
        return redirect(url_for("login"))
    
    review = Review.query.get_or_404(review_id)
    
    # Check if review belongs to current user
    if review.user_id != session['user_id']:
        flash("You can only edit your own reviews!", "error")
        return redirect(url_for("game_review", game_id=game_id))
    
    comment = request.form.get('comment', '').strip()
    rating = request.form.get('rating')
    
    if not comment:
        flash("Comment cannot be empty!", "error")
        return redirect(url_for("game_review", game_id=game_id))
    
    # Update review
    review.comment = comment
    review.rating = float(rating) if rating else None
    review.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    flash("Review updated successfully!", "success")
    return redirect(url_for("game_review", game_id=game_id))


@app.route("/game/<int:game_id>/delete-review/<int:review_id>", methods=["POST"])
def delete_review(game_id, review_id):
    if not session.get('user_id'):
        flash("Please login to delete a review!", "error")
        return redirect(url_for("login"))
    
    review = Review.query.get_or_404(review_id)
    
    # Check if review belongs to current user
    if review.user_id != session['user_id']:
        flash("You can only delete your own reviews!", "error")
        return redirect(url_for("game_review", game_id=game_id))
    
    db.session.delete(review)
    db.session.commit()
    
    flash("Review deleted successfully!", "success")
    return redirect(url_for("game_review", game_id=game_id))


# ================= CART =================
@app.route("/add_to_cart/<int:game_id>", methods=["POST"])
def add_to_cart(game_id):
    init_cart()
    cart = session["cart"]
    cart[str(game_id)] = cart.get(str(game_id), 0) + 1
    session["cart"] = cart
    return redirect(url_for("cart"))


@app.route("/cart")
def cart():
    init_cart()
    cart_data = []
    total_price = Decimal("0.00")

    for game_id, qty in session["cart"].items():
        game = Game.query.get(int(game_id))
        if game:
            subtotal = Decimal(game.price) * qty
            total_price += subtotal
            cart_data.append({"game": game, "quantity": qty, "subtotal": subtotal})
    
    user = None
    if session.get('user_id'):
        user = User.query.get(session['user_id'])

    return render_template("cart.html", cart_items=cart_data, total_price=total_price, user=user)


@app.route('/update_cart/<int:game_id>', methods=['POST'])
def update_cart(game_id):
    quantity = int(request.form.get('quantity', 1))
    init_cart()
    cart = session['cart']
    if str(game_id) in cart:
        cart[str(game_id)] = quantity
        session['cart'] = cart
    return redirect(url_for('cart'))


@app.route('/remove_from_cart/<int:game_id>', methods=['POST'])
def remove_from_cart(game_id):
    init_cart()
    if str(game_id) in session["cart"]:
        del session["cart"][str(game_id)]
        session.modified = True
    return redirect(url_for('cart'))


# ================= PROFILE =================
@app.route("/profile")
def profile():
    if not session.get("user_id"):
        flash("Please login to view your profile!", "error")
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    if not user:
        flash("User not found!", "error")
        session.clear()
        return redirect(url_for("login"))
    
    return render_template("profile.html", user=user)


@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():
    if not session.get("user_id"):
        flash("Please login to edit your profile!", "error")
        return redirect(url_for("login"))
    
    user = User.query.get(session["user_id"])
    if not user:
        flash("User not found!", "error")
        session.clear()
        return redirect(url_for("login"))
    
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        # Handle profile photo upload
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and file.filename and allowed_file(file.filename):
                # Create upload directory if it doesn't exist
                upload_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
                os.makedirs(upload_dir, exist_ok=True)
                
                # Generate unique filename
                filename = f"user_{user.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.{file.filename.rsplit('.', 1)[1].lower()}"
                filepath = os.path.join(upload_dir, filename)
                file.save(filepath)
                
                # Delete old photo if exists
                if user.profile_photo:
                    old_filepath = os.path.join(app.root_path, 'static', user.profile_photo)
                    if os.path.exists(old_filepath):
                        try:
                            os.remove(old_filepath)
                        except:
                            pass
                
                # Update user profile photo path
                user.profile_photo = f"uploads/profiles/{filename}"
        
        # Update username if provided
        if username and username != user.username:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user and existing_user.id != user.id:
                flash("Username already taken!", "error")
                return redirect(url_for("edit_profile"))
            user.username = username
        
        # Update email if provided
        if email and email != user.email:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != user.id:
                flash("Email already taken!", "error")
                return redirect(url_for("edit_profile"))
            user.email = email
        
        # Update password if provided
        if new_password:
            if not current_password:
                flash("Please enter current password to change password!", "error")
                return redirect(url_for("edit_profile"))
            
            if not check_password_hash(user.password, current_password):
                flash("Current password is incorrect!", "error")
                return redirect(url_for("edit_profile"))
            
            if new_password != confirm_password:
                flash("New passwords do not match!", "error")
                return redirect(url_for("edit_profile"))
            
            user.password = generate_password_hash(new_password)
            flash("Password updated successfully!", "success")
        
        db.session.commit()
        session["username"] = user.username
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))
    
    return render_template("edit_profile.html", user=user)


@app.route("/library")
def library():
    if not session.get("user_id"):
        flash("Please login to view your library!", "error")
        return redirect(url_for("login"))
    
    user = User.query.get(session["user_id"])
    if not user:
        flash("User not found!", "error")
        session.clear()
        return redirect(url_for("login"))
    
    # Get all purchased games from completed orders
    purchased_games = []
    for order in user.orders:
        if order.order_status == "Completed" or order.order_status == "Processing":
            for item in order.items:
                purchased_games.append({
                    "title": item.game.title,
                    "category": item.game.category,
                    "date_acquired": order.order_date,
                    "game": item.game
                })
    
    # Sort by date (most recent first)
    purchased_games.sort(key=lambda x: x["date_acquired"], reverse=True)
    
    # Handle sorting
    sort_by = request.args.get("sort", "date")
    if sort_by == "title":
        purchased_games.sort(key=lambda x: x["title"].lower())
    elif sort_by == "genre" or sort_by == "category":
        purchased_games.sort(key=lambda x: x["category"] or "")
    
    return render_template("library.html", games=purchased_games, sort=sort_by)


@app.route("/notifications")
def notifications():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    
    user = User.query.get(session["user_id"])
    notifications_list = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).all()
    
    return render_template("notifications.html", notes=notifications_list)


@app.route("/mark-all-read", methods=["POST"])
def mark_all_read():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    
    user = User.query.get(session["user_id"])
    Notification.query.filter_by(user_id=user.id, is_read=False).update({"is_read": True})
    db.session.commit()
    
    flash("All notifications marked as read!", "success")
    return redirect(url_for("notifications"))


@app.route("/read-notification/<int:n_id>")
def read_notification(n_id):
    if not session.get("user_id"):
        return redirect(url_for("login"))
    
    notification = Notification.query.get_or_404(n_id)
    if notification.user_id != session["user_id"]:
        flash("Unauthorized access!", "error")
        return redirect(url_for("notifications"))
    
    notification.is_read = True
    db.session.commit()
    
    return redirect(url_for("notifications"))


# ================= CHECKOUT =================
@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    init_cart()
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    cart_data = []
    total_price = Decimal("0.00")

    for game_id, qty in session["cart"].items():
        game = Game.query.get(int(game_id))
        subtotal = Decimal(game.price) * qty
        total_price += subtotal
        cart_data.append({"game": game, "quantity": qty, "subtotal": subtotal})

    if request.method == "POST":
        if user.balance >= total_price:
            new_order = Order(user_id=user.id, total_price=total_price)
            db.session.add(new_order)
            db.session.commit()

            for item in cart_data:
                db.session.add(OrderItem(
                    order_id=new_order.id,
                    game_id=item["game"].id,
                    quantity=item["quantity"],
                    price_at_purchase=item["game"].price
                ))
                
                # Create notification for each purchased game
                notification = Notification(
                    user_id=user.id,
                    message=f"You purchased {item['game'].title} for ${item['game'].price:.2f} on {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
                    is_read=False
                )
                db.session.add(notification)

            user.balance -= total_price
            db.session.commit()

            session["cart"] = {}
            return redirect(url_for("checkout_success"))

        else:
            return "<h2>Insufficient balance!</h2>"

    return render_template("checkout.html", cart_items=cart_data, total_price=total_price, user=user)


@app.route("/checkout_success")
def checkout_success():
    return "<h2>Order placed successfully!</h2>"


# ================= ADMIN =================
def admin_required(f):
    """Decorator to require admin authentication"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash("Admin access required!", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    users_count = User.query.count()
    games_count = Game.query.count()
    orders_count = Order.query.count()
    recent_orders = Order.query.order_by(Order.order_date.desc()).limit(5).all()
    
    return render_template("admin_dashboard.html", 
                         users_count=users_count,
                         games_count=games_count,
                         orders_count=orders_count,
                         recent_orders=recent_orders)


@app.route("/admin/games")
@admin_required
def admin_games():
    games = Game.query.order_by(Game.date_added.desc()).all()
    return render_template("admin_games.html", games=games)


@app.route("/admin/games/add", methods=["GET", "POST"])
@admin_required
def admin_add_game():
    if request.method == "POST":
        title = request.form.get("title")
        category = request.form.get("category") or request.form.get("genre")
        price = Decimal(request.form.get("price", 0))
        rating = float(request.form.get("rating", 0)) if request.form.get("rating") else None
        downloads = int(request.form.get("downloads", 0)) if request.form.get("downloads") else 0
        image = request.form.get("image") or request.form.get("image_url")
        
        if not image:
            image = "assets/images/default.jpg"
        
        new_game = Game(
            title=title,
            category=category,
            price=price,
            rating=rating,
            downloads=downloads,
            image=image
        )
        
        db.session.add(new_game)
        db.session.commit()
        
        # Log activity
        if session.get('admin_id'):
            activity = ActivityLog(
                admin_id=session['admin_id'],
                action="Added game",
                target_type="Game",
                target_id=new_game.id,
                details=f"Added game: {title}"
            )
            db.session.add(activity)
            db.session.commit()
        
        flash("Game added successfully!", "success")
        return redirect(url_for("admin_games"))
    
    return render_template("admin_add_game.html")


@app.route("/admin/games/<int:game_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_game(game_id):
    game = Game.query.get_or_404(game_id)
    
    if request.method == "POST":
        game.title = request.form.get("title")
        game.category = request.form.get("category") or request.form.get("genre")
        game.price = Decimal(request.form.get("price", 0))
        if request.form.get("rating"):
            game.rating = float(request.form.get("rating"))
        if request.form.get("downloads"):
            game.downloads = int(request.form.get("downloads"))
        if request.form.get("image") or request.form.get("image_url"):
            game.image = request.form.get("image") or request.form.get("image_url")
        
        db.session.commit()
        
        # Log activity
        if session.get('admin_id'):
            activity = ActivityLog(
                admin_id=session['admin_id'],
                action="Edited game",
                target_type="Game",
                target_id=game.id,
                details=f"Edited game: {game.title}"
            )
            db.session.add(activity)
            db.session.commit()
        
        flash("Game updated successfully!", "success")
        return redirect(url_for("admin_games"))
    
    return render_template("admin_edit_game.html", game=game)


@app.route("/admin/games/<int:game_id>/delete", methods=["POST"])
@admin_required
def admin_delete_game(game_id):
    game = Game.query.get_or_404(game_id)
    game_title = game.title
    
    db.session.delete(game)
    db.session.commit()
    
    # Log activity
    if session.get('admin_id'):
        activity = ActivityLog(
            admin_id=session['admin_id'],
            action="Deleted game",
            target_type="Game",
            target_id=game_id,
            details=f"Deleted game: {game_title}"
        )
        db.session.add(activity)
        db.session.commit()
    
    flash("Game deleted successfully!", "success")
    return redirect(url_for("admin_games"))


@app.route("/admin/users")
@admin_required
def admin_users():
    query = request.args.get("q", "")
    if query:
        users = User.query.filter(
            (User.username.ilike(f"%{query}%")) | 
            (User.email.ilike(f"%{query}%"))
        ).all()
    else:
        users = User.query.all()
    
    return render_template("admin_users.html", users=users, q=query)


@app.route("/admin/users/<int:user_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == "POST":
        user.username = request.form.get("username")
        user.email = request.form.get("email")
        user.account_status = request.form.get("account_status", "Active")
        if request.form.get("balance"):
            user.balance = Decimal(request.form.get("balance"))
        
        db.session.commit()
        
        # Log activity
        if session.get('admin_id'):
            activity = ActivityLog(
                admin_id=session['admin_id'],
                action="Edited user",
                target_type="User",
                target_id=user.id,
                details=f"Edited user: {user.username}"
            )
            db.session.add(activity)
            db.session.commit()
        
        flash("User updated successfully!", "success")
        return redirect(url_for("admin_users"))
    
    return render_template("admin_edit_user.html", user=user)


@app.route("/admin/orders")
@admin_required
def admin_orders():
    orders = Order.query.order_by(Order.order_date.desc()).all()
    total_orders = Order.query.count()
    total_revenue = sum([order.total_price for order in Order.query.filter_by(order_status="Completed").all()])
    completed_count = Order.query.filter_by(order_status="Completed").count()
    cancelled_count = Order.query.filter_by(order_status="Cancelled").count()
    
    return render_template("admin_orders.html",
                           orders=orders,
                           total_orders=total_orders,
                           total_revenue=total_revenue,
                           completed_count=completed_count,
                           cancelled_count=cancelled_count)


@app.route("/admin/orders/<int:order_id>", methods=["GET", "POST"])
@admin_required
def admin_order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    
    if request.method == "POST":
        order.order_status = "Cancelled"
        db.session.commit()
        
        # Log activity
        if session.get('admin_id'):
            activity = ActivityLog(
                admin_id=session['admin_id'],
                action="Cancelled order",
                target_type="Order",
                target_id=order.id,
                details=f"Cancelled order #{order.id}"
            )
            db.session.add(activity)
            db.session.commit()
        
        flash("Order cancelled!", "success")
        return redirect(url_for("admin_orders"))
    
    return render_template("admin_order_detail.html", order=order)


@app.route("/admin/activity")
@admin_required
def admin_activity():
    activities = ActivityLog.query.order_by(ActivityLog.date.desc()).limit(50).all()
    return render_template("admin_activity.html", activities=activities)


if __name__ == "__main__":
    app.run(debug=True)
