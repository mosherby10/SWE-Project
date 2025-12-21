"""
Application Factory Pattern
Creates and configures the Flask application instance
"""
from flask import Flask
from models.database import db
import os


def create_app(config_name='development'):
    """
    Application factory function
    Creates and configures Flask app instance
    """
    app = Flask(__name__, template_folder='views', static_folder='static')
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///gaming_store.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/uploads/profiles'
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours - for theme/language persistence
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Add context processor for theme and language
    @app.context_processor
    def inject_theme_and_language():
        from flask import session
        return {
            'current_theme': session.get('theme', 'dark'),
            'current_language': session.get('language', 'en')
        }
    
    # Initialize database
    with app.app_context():
        init_database(app)
    
    return app


def register_blueprints(app):
    """Register all application blueprints"""
    from controllers.home_controller import home_bp
    from controllers.auth_controller import auth_bp
    from controllers.browse_controller import browse_bp
    from controllers.cart_controller import cart_bp
    from controllers.profile_controller import profile_bp
    from controllers.admin_controller import admin_bp
    from controllers.support_controller import support_bp
    from controllers.review_controller import review_bp
    from controllers.about_controller import about_bp
    from controllers.wishlist_controller import wishlist_bp
    from controllers.theme_controller import theme_bp
    from controllers.language_controller import language_bp
    
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(browse_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(support_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(about_bp)
    app.register_blueprint(wishlist_bp)
    app.register_blueprint(theme_bp)
    app.register_blueprint(language_bp)


def init_database(app):
    """Initialize database with default data"""
    from models import User, Game, Admin
    from werkzeug.security import generate_password_hash
    from decimal import Decimal
    
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

