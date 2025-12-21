from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from decimal import Decimal

db = SQLAlchemy()

# -------------------------
# USERS
# -------------------------
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    account_status = db.Column(db.String(20), default="Active")
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    balance = db.Column(db.Numeric(10, 2), default=Decimal("100.00"))
    profile_photo = db.Column(db.String(255), nullable=True)  # Path to profile photo

    orders = db.relationship("Order", backref="user", lazy=True)
    reviews = db.relationship("Review", backref="user", cascade="all, delete-orphan", lazy=True)
    notifications = db.relationship("Notification", backref="user", cascade="all, delete-orphan", lazy=True)


# -------------------------
# ADMINS
# -------------------------
class Admin(db.Model):
    __tablename__ = "admins"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


# -------------------------
# GAMES
# -------------------------
class Game(db.Model):
    __tablename__ = "games"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100))
    price = db.Column(db.Numeric(10, 2))
    rating = db.Column(db.Float, default=0.0)
    downloads = db.Column(db.Integer, default=0)
    image = db.Column(db.String(255))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    reviews = db.relationship("Review", backref="game", cascade="all, delete-orphan", lazy=True)


# -------------------------
# ORDERS
# -------------------------
class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_price = db.Column(db.Numeric(10, 2))
    order_status = db.Column(db.String(20), default="Processing")

    items = db.relationship("OrderItem", backref="order", cascade="all, delete-orphan", lazy=True)


class OrderItem(db.Model):
    __tablename__ = "order_items"
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Numeric(10, 2))

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


# -------------------------
# PASSWORD RESET TOKENS
# -------------------------
class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(6), nullable=False)  # 6-digit code
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)


# -------------------------
# REVIEWS
# -------------------------
class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float)  # Optional rating (1-5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# -------------------------
# NOTIFICATIONS
# -------------------------
class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)