from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Game, Order, OrderItem
from decimal import Decimal
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gaming_store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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


# ================= CART SESSION INIT =================
def init_cart():
    if "cart" not in session:
        session["cart"] = {}


# ================= HOME PAGE =================
@app.route("/")
def home():
    user_logged_in = 'user_id' in session
    username = session.get('username', '')
    return render_template("index.html", user_logged_in=user_logged_in, username=username)


# ================= AUTH =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
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
        flash("Account created successfully! Welcome to Game-verse!", "success")
        return redirect(url_for("home"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for("home"))


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        flash("If account exists, reset link sent!", "success")
        return render_template("forgot_password.html", success=True)

    return render_template("forgot_password.html")


# ================= BROWSE =================
@app.route("/browse")
def browse():
    query = request.args.get("q", "")
    games = Game.query.filter(Game.title.ilike(f"%{query}%")).all() if query else Game.query.all()
    return render_template("browse.html", games=games)


@app.route("/game/<int:game_id>")
def game_review(game_id):
    game = Game.query.get_or_404(game_id)
    comments = []
    return render_template("game_review.html", game=game, comments=comments)


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

    return render_template("cart.html", cart_items=cart_data, total_price=total_price)


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
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    return render_template("profile.html", user=user)


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


if __name__ == "__main__":
    app.run(debug=True)
