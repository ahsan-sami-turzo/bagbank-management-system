#!/usr/bin/env bash

# ===============================
# BagBank Management System Setup Script
# Compatible with Linux, macOS, and Windows (Git Bash)
# ===============================

set -e

# Utility for colored output
print_step() { echo -e "\n\033[1;36m$1\033[0m"; }
print_done() { echo -e "✅ $1\n"; }

PROJECT_DIR="bagbank-management-system"

print_step "🚀 Setting up Flask BagBank Management System..."

# -------------------------------
# Create main project directory
# -------------------------------
if [ ! -d "$PROJECT_DIR" ]; then
    mkdir -p "$PROJECT_DIR"
fi
cd "$PROJECT_DIR"

# -------------------------------
# Create Python Virtual Environment
# -------------------------------
print_step "🐍 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv || python -m venv venv
    print_done "Virtual environment created."
else
    echo "⚠️ Virtual environment already exists."
fi

# Detect correct Python executable inside venv
if [ -f "venv/bin/python" ]; then
    PYTHON="venv/bin/python"
elif [ -f "venv/Scripts/python.exe" ]; then
    PYTHON="venv/Scripts/python.exe"
else
    echo "❌ Could not locate Python in virtual environment."
    exit 1
fi

# -------------------------------
# Create directory structure
# -------------------------------
print_step "📁 Creating project structure..."

mkdir -p app/templates instance migrations

cat > .env << 'EOF'
SECRET_KEY='your_super_secret_key_that_you_must_change_now!'
SQLALCHEMY_DATABASE_URI='sqlite:///instance/bbms.sqlite'
SUPERADMIN_USERNAME='superadmin'
SUPERADMIN_PASSWORD='superadmin'
SUPERADMIN_EMAIL='sysadmin@bagbank.com'
EOF

cat > config.py << 'EOF'
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SUPERADMIN_USERNAME = os.environ.get('SUPERADMIN_USERNAME')
    SUPERADMIN_PASSWORD = os.environ.get('SUPERADMIN_PASSWORD')
    SUPERADMIN_EMAIL = os.environ.get('SUPERADMIN_EMAIL')

    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
EOF

cat > requirements.txt << 'EOF'
Flask
Flask-SQLAlchemy
Flask-Migrate
Flask-Login
Flask-WTF
Flask-Bcrypt
python-dotenv
Bootstrap-Flask
EOF

cat > requirements-dev.txt << 'EOF'
black
flake8
pytest
ipython
EOF

cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*.sqlite
*.log

# Environments
venv/
.env

# Flask / Alembic
instance/
migrations/
EOF

cat > app.py << 'EOF'
from app import create_app, db
from app.models import User
from flask_migrate import Migrate
import click

app = create_app()
migrate = Migrate(app, db)

@app.cli.command("init_db")
@click.option("--reset", is_flag=True, help="Reset the database before creating the SuperAdmin.")
def init_db(reset):
    with app.app_context():
        if reset:
            db.drop_all()
            click.echo("INFO: Dropped all existing tables.")
        db.create_all()
        click.echo("INFO: Database tables created.")
        username = app.config['SUPERADMIN_USERNAME']
        if not User.query.filter_by(username=username).first():
            super_admin = User(
                role=0,
                name="System Superadmin",
                phone="0000000000",
                email=app.config['SUPERADMIN_EMAIL'],
                username=username
            )
            super_admin.set_password(app.config['SUPERADMIN_PASSWORD'])
            db.session.add(super_admin)
            db.session.commit()
            click.echo(f"SUCCESS: Initial SuperAdmin '{username}' created.")
        else:
            click.echo("INFO: SuperAdmin already exists.")
if __name__ == '__main__':
    app.run()
EOF

mkdir -p app
cat > app/__init__.py << 'EOF'
import os
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from bootstrap_flask import Bootstrap5

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
csrf = CSRFProtect()
bootstrap = Bootstrap5()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    bootstrap.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'
    login_manager.login_message = 'Please log in to access this page.'
    from app import routes
    app.register_blueprint(routes.bp)
    os.makedirs(app.instance_path, exist_ok=True)
    return app
EOF

cat > app/routes.py << 'EOF'
from flask import Blueprint, render_template
bp = Blueprint('routes', __name__)
@bp.route('/')
def dashboard():
    return render_template('dashboard.html')
EOF

cat > app/models.py << 'EOF'
from app import db, bcrypt
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.Integer, default=1)
    name = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
EOF

mkdir -p app/templates
cat > app/templates/base.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>BagBank Management System</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <a class="navbar-brand ms-3" href="/">BagBank</a>
  </nav>
  <div class="container mt-4">
    {% block content %}{% endblock %}
  </div>
</body>
</html>
EOF

cat > app/templates/dashboard.html << 'EOF'
{% extends 'base.html' %}
{% block content %}
<h1 class="mb-4">Welcome to BagBank Management System</h1>
<p class="text-muted">System initialized successfully.</p>
{% endblock %}
EOF

# -------------------------------
# Install dependencies
# -------------------------------
print_step "📦 Installing dependencies..."
"$PYTHON" -m pip install --upgrade pip
"$PYTHON" -m pip install -r requirements.txt -r requirements-dev.txt
print_done "Dependencies installed."

# -------------------------------
# Final message
# -------------------------------
echo -e "\n🎉 Setup complete!"
echo "➡ To start your app:"
echo "cd $PROJECT_DIR"
echo "source venv/bin/activate   # (or venv\\Scripts\\activate on Windows)"
echo "flask --app app.py init_db"
echo "flask --app app.py run"
