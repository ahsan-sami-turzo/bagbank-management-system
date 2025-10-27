# app/utils.py

from functools import wraps
from flask_login import current_user
from flask import abort

def superadmin_required(f):
    """Decorator to allow only SuperAdmin users (Role 0) to access a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # We must assume the User model's role checks are correct (Role 0 = SuperAdmin)
        if not current_user.is_authenticated or current_user.role != 0:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def admin_or_superadmin_required(f):
    """Decorator to allow only Admin (Role 1) or SuperAdmin (Role 0) users to access a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # We must assume the User model's role checks are correct (Role 0 or 1)
        if not current_user.is_authenticated or current_user.role not in [0, 1]:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to allow only Admin users (Role 1) to access a route for CRUD operations."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Explicitly check for Admin role (1)
        if not current_user.is_authenticated or current_user.role != 1:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function