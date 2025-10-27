# utils.py

from functools import wraps


# ----------------------------
# Access Control Decorators
# ----------------------------
def admin_or_superadmin_required(f):
    """Decorator to allow only Admin or SuperAdmin users to access a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user
        if not current_user.is_authenticated or not current_user.is_admin_or_superadmin():
            from flask import abort
            abort(403)
        return f(*args, **kwargs)
    return decorated_function