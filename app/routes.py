from flask import (
    Blueprint, render_template, redirect, url_for, flash, request
)
from flask_login import login_user, current_user, logout_user, login_required
from app.forms import LoginForm, UserForm 
from app.models import User, USER_ROLES
from app import db 
from functools import wraps
from flask import abort


bp = Blueprint('main', __name__)


# --- Access Control Decorator (Must be defined here or imported) ---
def superadmin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_superadmin():
            abort(403) 
        return f(*args, **kwargs)
    return decorated_function
# -----------------------------------------------------------------


# --- LOGIN ROUTE ---
@bp.route('/', methods=['GET', 'POST'])
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Allow login via username or email
        user = User.query.filter((User.username == form.username.data) | (User.email == form.username.data)).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            # Redirect to the page they were trying to access, or the dashboard
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('Login Unsuccessful. Check username/email and password.', 'danger')

    return render_template('login.html', form=form, title='Login')

# --- DASHBOARD ROUTE ---
@bp.route('/dashboard')
@login_required # This decorator ensures only logged-in users can access
def dashboard():
    return render_template('dashboard.html', title='Dashboard')

# --- LOGOUT ROUTE ---
@bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

# --- User Management routes ---
# --- READ/VIEW Users ---
@bp.route('/users')
@login_required
@superadmin_required
def user_management():
    # Fetch all users except the currently logged-in SuperAdmin
    # Only show Admin (role=1) and Moderator (role=2)
    users = User.query.filter(User.role.in_([1, 2])).all() 
    return render_template('user_management.html', users=users, roles=USER_ROLES, title='User Management')

# --- CREATE/UPDATE User ---
@bp.route('/user/edit', defaults={'user_id': None}, methods=['GET', 'POST'])
@bp.route('/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@superadmin_required
def edit_user(user_id):
    user = None
    if user_id:
        user = db.get_or_404(User, user_id)
        # Prevent editing the SuperAdmin account from this interface
        if user.is_superadmin():
             flash('Cannot edit the SuperAdmin account via this interface.', 'danger')
             return redirect(url_for('main.user_management'))
        form = UserForm(obj=user)
        # Store the original user object for unique field validation
        form.original_user = user 
        
    else:
        form = UserForm()
        
    if form.validate_on_submit():
        if user: # Edit existing user
            user.name = form.name.data
            user.phone = form.phone.data
            user.email = form.email.data
            user.username = form.username.data
            user.role = form.role.data
            
            if form.password.data:
                user.set_password(form.password.data)
            
            flash('User updated successfully.', 'success')
            
        else: # Create new user
            new_user = User(
                name=form.name.data,
                phone=form.phone.data,
                email=form.email.data,
                username=form.username.data,
                role=form.role.data
            )
            new_user.set_password(form.password.data if form.password.data else 'password') # Set a default password if none is provided
            db.session.add(new_user)
            flash('New user created successfully.', 'success')
            
        db.session.commit()
        return redirect(url_for('main.user_management'))
    
    # Pre-fill form on GET request for editing
    return render_template('user_edit.html', form=form, user=user, title='Add/Edit User')

# --- DELETE User ---
@bp.route('/user/delete/<int:user_id>', methods=['POST'])
@login_required
@superadmin_required
def delete_user(user_id):
    user = db.get_or_404(User, user_id)
    
    # Prevent deletion of SuperAdmin
    if user.is_superadmin():
        flash('Cannot delete the SuperAdmin account.', 'danger')
        return redirect(url_for('main.user_management'))

    db.session.delete(user)
    db.session.commit()
    flash(f'User "{user.username}" deleted successfully.', 'success')
    return redirect(url_for('main.user_management'))