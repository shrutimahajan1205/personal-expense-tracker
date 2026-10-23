from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import datetime

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access your expense tracker.'
login_manager.login_message_category = 'warning'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Template filters and context processors
    @app.context_processor
    def inject_now():
        return {
            'now': datetime.datetime.now(),
            'current_year': datetime.datetime.now().year
        }

    @app.template_filter('currency')
    def format_currency(value, symbol='₹'):
        if value is None:
            return f"{symbol}0.00"
        try:
            return f"{symbol}{float(value):,.2f}"
        except (ValueError, TypeError):
            return f"{symbol}0.00"

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.expenses import expenses_bp
    from app.routes.analytics import analytics_bp
    from app.routes.budgets import budgets_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(budgets_bp)

    # Create tables if not present
    with app.app_context():
        db.create_all()

    return app
