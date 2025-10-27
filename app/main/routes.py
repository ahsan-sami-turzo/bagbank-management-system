# app/main/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from functools import wraps
from app import db
from app.models import User, USER_ROLES
from app.forms import LoginForm, UserForm

# Import the BP defined in app/__init__.py
from app.main import bp 
from flask_login import current_user, login_user, logout_user, login_required

# ----------------------------
# Access Control Decorators
# ----------------------------
def superadmin_required(f):
    """Decorator to allow only SuperAdmin users to access a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_superadmin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/test')
def test():
    return "Main blueprint is working!"

# ----------------------------
# Authentication Routes
# ----------------------------
@bp.route('/', methods=['GET', 'POST'])
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.username.data)
        ).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Welcome back, {user.name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        flash('Login Unsuccessful. Check username/email and password.', 'danger')

    return render_template('login.html', form=form, title='Login')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))


# ----------------------------
# Dashboard
# ----------------------------
@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard')


# ----------------------------
# User Management
# ----------------------------
@bp.route('/users')
@login_required
@superadmin_required
def user_management():
    """View all Admin and Moderator users (exclude SuperAdmin)."""
    users = User.query.filter(User.role.in_([1, 2])).all()
    return render_template('user_management.html', users=users, roles=USER_ROLES, title='User Management')


@bp.route('/user/edit', defaults={'user_id': None}, methods=['GET', 'POST'])
@bp.route('/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@superadmin_required
def edit_user(user_id):
    """Create or edit a user."""
    user = db.get_or_404(User, user_id) if user_id else None
    if user and user.is_superadmin():
        flash('Cannot edit the SuperAdmin account via this interface.', 'danger')
        return redirect(url_for('main.user_management'))

    form = UserForm(obj=user)
    if user:
        form.original_user = user  # Needed for unique field validation

    if form.validate_on_submit():
        if user:
            form.populate_obj(user)
            if form.password.data:
                user.set_password(form.password.data)
            flash('User updated successfully.', 'success')
        else:
            new_user = User(
                name=form.name.data,
                phone=form.phone.data,
                email=form.email.data,
                username=form.username.data,
                role=form.role.data
            )
            new_user.set_password(form.password.data or 'password')
            db.session.add(new_user)
            flash('New user created successfully.', 'success')

        db.session.commit()
        return redirect(url_for('main.user_management'))

    return render_template('user_edit.html', form=form, user=user, title='Add/Edit User')


@bp.route('/user/delete/<int:user_id>', methods=['POST'])
@login_required
@superadmin_required
def delete_user(user_id):
    """Delete a user."""
    user = db.get_or_404(User, user_id)
    if user.is_superadmin():
        flash('Cannot delete the SuperAdmin account.', 'danger')
        return redirect(url_for('main.user_management'))

    db.session.delete(user)
    db.session.commit()
    flash(f'User "{user.username}" deleted successfully.', 'success')
    return redirect(url_for('main.user_management'))
