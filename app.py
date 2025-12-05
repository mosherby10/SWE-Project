from flask import Flask
from models import db
from admin import bp as admin_bp

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///store.db"
app.config["SECRET_KEY"] = "12345"

db.init_app(app)

app.register_blueprint(admin_bp)

# Create tables
with app.app_context():
    db.create_all()

# TEMPORARY admin login
from flask import session, redirect, url_for

@app.route("/admin_login")
def admin_login():
    session["admin_id"] = 1   # Store a real session
    return redirect(url_for("admin.dashboard"))


if __name__ == "__main__":
    app.run(debug=True)

