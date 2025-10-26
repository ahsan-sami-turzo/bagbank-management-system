from app import db, bcrypt
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

# Roles: 0 = SuperAdmin, 1 = Admin, 2 = Moderator
USER_ROLES = {0: 'SuperAdmin', 1: 'Admin', 2: 'Moderator'}

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.Integer, default=2, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    # NEW: Use bcrypt for hashing
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # NEW: Use bcrypt for checking
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User {self.username}>"

    # Add this method for template
    def get_role_name(self):
        """Return human-readable role name."""
        if self.role == "superadmin":
            return "Super Admin"
        elif self.role == "admin":
            return "Admin"
        else:
            return "User"

    # Optional helper for template sidebar
    def is_superadmin(self):
        return self.role == "superadmin"
