from functools import wraps
from flask import session, redirect, url_for, flash
from models import db, ActivityLog



def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "admin_id" not in session:
            flash("Admin login required")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return wrap

def log_activity(admin_id, action, target_type=None, target_id=None, details=None):
    log = ActivityLog(
        admin_id=admin_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details
    )
    db.session.add(log)
    db.session.commit()
