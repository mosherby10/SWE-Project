from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# -------------------------
# USERS
# -------------------------
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    account_status = db.Column(db.String(20), default="Active")
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


# -------------------------
# ADMINS
# -------------------------
class Admin(db.Model):
    __tablename__ = "admins"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))


# -------------------------
# GAMES
# -------------------------
class Game(db.Model):
    __tablename__ = "games"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    price = db.Column(db.Numeric(10,2))


# -------------------------
# ORDERS
# -------------------------
class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_price = db.Column(db.Numeric(10,2))
    order_status = db.Column(db.String(20), default="Processing")

    # Relationships
    user = db.relationship("User", backref="orders")
    items = db.relationship("OrderItem", backref="order", cascade="all, delete-orphan")


class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    quantity = db.Column(db.Integer)
    price_at_purchase = db.Column(db.Numeric(10,2))

    game = db.relationship("Game")


# -------------------------
# ACTIVITY LOGS
# -------------------------
class ActivityLog(db.Model):
    __tablename__ = "activity_logs"
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer)
    action = db.Column(db.String(255))
    target_type = db.Column(db.String(50))
    target_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
