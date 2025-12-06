from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"
USER_ID = 1  


def query_db(query, params=(), one=False):
    conn = sqlite3.connect("app.db")
    c = conn.cursor()
    c.execute(query, params)
    rv = c.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv


@app.route("/")
def home():
    return redirect(url_for("profile"))


@app.route("/profile")
def profile():
    # Fetch username (index 0), name (index 1), country (index 2), bio (index 3), avatar (index 4)
    user = query_db("SELECT username, name, country, bio, avatar FROM users WHERE id=?", (USER_ID,), one=True)
    return render_template("profile.html", user=user)

@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if request.method == "POST":
        # New: Get username from the form
        username = request.form["username"]
        name = request.form["name"]
        country = request.form["country"]
        bio = request.form["bio"]

        avatar = None
        if "avatar" in request.files:
            file = request.files["avatar"]
            if file.filename != "":
                # Save the new avatar file
                avatar = file.filename
                # Ensure the upload folder exists
                if not os.path.exists(app.config["UPLOAD_FOLDER"]):
                    os.makedirs(app.config["UPLOAD_FOLDER"])
                file.save(os.path.join(app.config["UPLOAD_FOLDER"], avatar))

        if avatar:
            # Update all fields including username and new avatar
            query_db("UPDATE users SET username=?, name=?, country=?, bio=?, avatar=? WHERE id=?",
                     (username, name, country, bio, avatar, USER_ID))
        else:
            # Update all fields including username, keeping old avatar
            query_db("UPDATE users SET username=?, name=?, country=?, bio=? WHERE id=?",
                     (username, name, country, bio, USER_ID))

        return redirect(url_for("profile"))

    # Fetch username (index 0), name (index 1), country (index 2), bio (index 3), avatar (index 4)
    user = query_db("SELECT username, name, country, bio, avatar FROM users WHERE id=?", (USER_ID,), one=True)
    return render_template("edit_profile.html", user=user)


@app.route("/notifications")
def notifications():
    notes = query_db(
        "SELECT id, message, is_read, created_at FROM notifications WHERE user_id=? ORDER BY id DESC",
        (USER_ID,)
    )
    return render_template("notifications.html", notes=notes)

@app.route("/notifications/read/<int:n_id>")
def read_notification(n_id):
    query_db("UPDATE notifications SET is_read=1 WHERE id=?", (n_id,))
    return redirect(url_for("notifications"))

@app.route("/notifications/mark_read", methods=["POST"])
def mark_all_read():
    query_db("UPDATE notifications SET is_read=1 WHERE user_id=?", (USER_ID,))
    return redirect(url_for("notifications"))

@app.route("/notifications/add")
def add_notification_test():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    query_db(
        "INSERT INTO notifications (user_id, message, created_at) VALUES (?, ?, ?)",
        (USER_ID, "Test notification!", now)
    )
    return redirect(url_for("notifications"))

@app.route("/library")
def library():
    sort = request.args.get("sort", "title")
    allowed_sorts = ["title", "genre", "date"]  
    if sort not in allowed_sorts:
        sort = "title"

    query = f"""
        SELECT games.title, games.genre, orders.date
        FROM order_items
        JOIN orders ON order_items.order_id = orders.id
        JOIN games ON order_items.game_id = games.id
        WHERE orders.user_id = ?
        ORDER BY {sort} ASC
    """
    games = query_db(query, (USER_ID,))
    return render_template("library.html", games=games, sort=sort)

if __name__ == "__main__":
    app.run(debug=True, port=5001)