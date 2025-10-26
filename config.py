import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Core Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = True  # Change to False for production

    # SQLAlchemy Configuration (Database Agnosticism is handled here)
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'bbbms.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Recommended to set to False

    # Custom App Configuration (Used for initial setup)
    SUPERADMIN_USERNAME = os.environ.get('SUPERADMIN_USERNAME')
    SUPERADMIN_PASSWORD = os.environ.get('SUPERADMIN_PASSWORD')
    SUPERADMIN_EMAIL = os.environ.get('SUPERADMIN_EMAIL')

    # File Uploads (for user photos, etc.)
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16 MB limit