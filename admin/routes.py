from flask import render_template, request, redirect, url_for, flash, session
from . import bp
from .utils import admin_required, log_activity
from models import db, User, Order, OrderItem, Game, ActivityLog
from datetime import datetime


# ---------------------------
# DASHBOARD
# ---------------------------
@bp.route("/dashboard")
@admin_required
def dashboard():
    return render_template(
        "admin_dashboard.html",
        users_count=User.query.count(),
        games_count=Game.query.count(),
        orders_count=Order.query.count(),
        recent_orders=Order.query.order_by(Order.order_date.desc()).limit(5)
    )

# ---------------------------
# USER MANAGEMENT
# ---------------------------
@bp.route("/users")
@admin_required
def users():
    q = request.args.get("q", "")
    users = User.query.filter(User.username.ilike(f"%{q}%")).all() if q else User.query.all()
    return render_template("admin_users.html", users=users, q=q)

@bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    admin_id = session["admin_id"]

    if request.method == "POST":
        action = request.form.get("action")

        if action == "ban":
            user.account_status = "Banned"
            db.session.commit()
            log_activity(admin_id, "ban_user", "user", user_id)
        elif action == "unban":
            user.account_status = "Active"
            db.session.commit()
            log_activity(admin_id, "unban_user", "user", user_id)
        elif action == "delete":
            db.session.delete(user)
            db.session.commit()
            log_activity(admin_id, "delete_user", "user", user_id)
            return redirect(url_for("admin.users"))
        else:
            user.username = request.form["username"]
            user.email = request.form["email"]
            db.session.commit()
            log_activity(admin_id, "edit_user", "user", user_id)

        return redirect(url_for("admin.edit_user", user_id=user_id))

    return render_template("admin_edit_user.html", user=user)

# ---------------------------
# ORDER MONITORING
# ---------------------------
# ---------------------------
# ORDERS LIST + SUMMARY
# ---------------------------
@bp.route("/orders", methods=["GET"])
@admin_required
def orders():
    orders = Order.query.order_by(Order.order_date.desc()).all()

    # Summary metrics
    total_orders = len(orders)
    total_revenue = sum(float(order.total_price or 0) for order in orders)
    pending_count = sum(1 for o in orders if o.order_status == "Processing")
    shipped_count = sum(1 for o in orders if o.order_status == "Shipped")
    completed_count = sum(1 for o in orders if o.order_status == "Completed")
    cancelled_count = sum(1 for o in orders if o.order_status == "Cancelled")

    return render_template(
        "admin_orders.html",
        orders=orders,
        total_orders=total_orders,
        total_revenue=total_revenue,
        pending_count=pending_count,
        shipped_count=shipped_count,
        completed_count=completed_count,
        cancelled_count=cancelled_count
    )

# ---------------------------
# ORDER DETAIL + CANCEL
# ---------------------------
@bp.route("/orders/<int:order_id>", methods=["GET", "POST"])
@admin_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)

    if request.method == "POST" and order.order_status != "Cancelled":
        order.order_status = "Cancelled"
        db.session.commit()
        log_activity(session["admin_id"], "cancel_order", "order", order.id,
                     f"Admin cancelled order #{order.id}")
        flash(f"Order #{order.id} has been cancelled.", "success")
        return redirect(url_for("admin.order_detail", order_id=order.id))

    return render_template("admin_order_detail.html", order=order)


# ---------------------------
# ACTIVITY LOG
# ---------------------------
@bp.route("/activity")
@admin_required
def activity_logs():
    logs = ActivityLog.query.order_by(ActivityLog.date.desc()).all()
    return render_template("admin_activity.html", logs=logs)

# ---------------------------
# GAME MANAGEMENT (CRUD)
# ---------------------------
@bp.route("/games")
@admin_required
def admin_games():
    q = request.args.get("q", "")
    games = Game.query.filter(Game.title.ilike(f"%{q}%")).all() if q else Game.query.all()
    return render_template("admin_games.html", games=games, q=q)

@bp.route("/games/add", methods=["GET", "POST"])
@admin_required
def add_game():
    if request.method == "POST":
        title = request.form["title"]
        price = request.form["price"]
        admin_id = session["admin_id"]

        if not title or not price:
            flash("All fields are required.", "danger")
            return redirect(url_for("admin.add_game"))

        game = Game(title=title, price=price)
        db.session.add(game)
        db.session.commit()
        log_activity(admin_id, "add_game", "game", game.id)
        flash("Game added successfully!", "success")
        return redirect(url_for("admin.admin_games"))

    return render_template("admin_add_game.html")

@bp.route("/games/<int:game_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_game(game_id):
    game = Game.query.get_or_404(game_id)
    admin_id = session["admin_id"]

    if request.method == "POST":
        game.title = request.form["title"]
        game.price = request.form["price"]
        db.session.commit()
        log_activity(admin_id, "edit_game", "game", game_id)
        flash("Game updated successfully!", "success")
        return redirect(url_for("admin.admin_games"))

    return render_template("admin_edit_game.html", game=game)

@bp.route("/games/<int:game_id>/delete", methods=["POST"])
@admin_required
def delete_game(game_id):
    game = Game.query.get_or_404(game_id)
    admin_id = session["admin_id"]
    db.session.delete(game)
    db.session.commit()
    log_activity(admin_id, "delete_game", "game", game_id)
    flash("Game deleted successfully!", "success")
    return redirect(url_for("admin.admin_games"))
