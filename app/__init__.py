import os
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_bootstrap import Bootstrap5

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
csrf = CSRFProtect()
bootstrap = Bootstrap5()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure instance folder exists (for SQLite database)
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    bootstrap.init_app(app)

    # Flask-Login settings
    login_manager.login_view = 'login'  # endpoint name for login
    login_manager.login_message_category = 'info'
    login_manager.login_message = 'Please log in to access this page.'

    # Import and register blueprints/routes
    from app import routes
    app.register_blueprint(routes.bp)  # Assuming you have a Blueprint called 'bp'

    # Register CLI commands
    register_cli_commands(app)

    # Setup Flask-Login user_loader
    setup_login_manager(app)

    return app

def setup_login_manager(app):
    """Configure Flask-Login user_loader."""
    from app.models import User  # import your User model here

    @login_manager.user_loader
    def load_user(user_id):
        """Load user for Flask-Login."""
        return User.query.get(int(user_id))

def register_cli_commands(app):
    """Register custom Flask CLI commands."""
    @app.cli.command("init_db")
    def init_db():
        """Create all tables in the database (development only)."""
        db.create_all()
        print("Database initialized!")

    @app.cli.command("migrate_db")
    def migrate_db():
        """Helper command to remind about Flask-Migrate workflow."""
        print("Use 'flask db migrate -m \"message\"' and 'flask db upgrade' for migrations.")
