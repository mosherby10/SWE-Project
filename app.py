from flask import Flask, render_template, request, redirect, url_for, session
from models import db, Game, Order, OrderItem, User
from decimal import Decimal

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gaming_store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# -------------------------
# إنشاء DB و Games تجريبية
# -------------------------
def create_tables():
    with app.app_context():
        db.create_all()
        if not Game.query.first():
            games = [
                Game(title="Fortnite", category="Sandbox", price=0, rating=4.8, downloads=2300000, image="assets/images/game-01.jpg"),
                Game(title="CS-GO", category="Legendary", price=0, rating=4.8, downloads=2300000, image="assets/images/game-02.jpg"),
                Game(title="PubG", category="Battle Royale", price=0, rating=4.7, downloads=2200000, image="assets/images/game-03.jpg"),
                Game(title="Dota2", category="MOBA", price=0, rating=4.9, downloads=2400000, image="assets/images/game-04.jpg"),
            ]
            for g in games:
                db.session.add(g)
            db.session.commit()

create_tables()

# -------------------------
# Get or create user's pending order
# -------------------------
def get_cart_order(user_id=1):
    order = Order.query.filter_by(user_id=user_id, order_status="Pending").first()
    if not order:
        order = Order(user_id=user_id, total_price=0)
        db.session.add(order)
        db.session.commit()
    return order

# -------------------------
# Routes
# -------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/browse")
def browse():
    query = request.args.get("q", "")
    if query:
        games = Game.query.filter(Game.title.ilike(f"%{query}%")).all()
    else:
        games = Game.query.all()
    return render_template("browse.html", games=games)

# -------------------------
# CART
# -------------------------
@app.route("/cart")
def cart():
    order = get_cart_order()
    cart_items = []
    total_price = Decimal("0.00")
    for item in order.items:
        subtotal = Decimal(item.price_at_purchase or 0) * item.quantity
        total_price += subtotal
        cart_items.append({"game": item.game, "quantity": item.quantity, "subtotal": subtotal, "item_id": item.id})
    return render_template("cart.html", cart_items=cart_items, total_price=total_price)

@app.route("/add_to_cart/<int:game_id>")
def add_to_cart(game_id):
    order = get_cart_order()
    game = Game.query.get(game_id)
    if game:
        # تحقق إذا اللعبة موجودة بالفعل
        existing_item = OrderItem.query.filter_by(order_id=order.id, game_id=game.id).first()
        if existing_item:
            existing_item.quantity += 1
        else:
            new_item = OrderItem(order_id=order.id, game_id=game.id, quantity=1, price_at_purchase=game.price)
            db.session.add(new_item)
        db.session.commit()
    return redirect(url_for("cart"))

@app.route("/remove_from_cart/<int:item_id>")
def remove_from_cart(item_id):
    item = OrderItem.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for("cart"))

@app.route("/update_cart", methods=["POST"])
def update_cart():
    for key, value in request.form.items():
        if key.startswith("qty_") and value.isdigit():
            item_id = int(key.split("_")[1])
            item = OrderItem.query.get(item_id)
            if item:
                if int(value) > 0:
                    item.quantity = int(value)
                else:
                    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("cart"))

@app.route("/checkout")
def checkout():
    order = get_cart_order()
    order.order_status = "Completed"
    db.session.commit()
    return "<h2>Checkout done! Your order is completed.</h2><a href='/browse'>Back to Browse</a>"

if __name__ == "__main__":
    app.run(debug=True)
