# app/user/routes.py

from flask import render_template, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import User, USER_ROLES
from app.forms import UserForm # Your UserForm is in forms.py
from app.user import bp 
from app.utils import superadmin_required, admin_required # Assuming access utility exists
from sqlalchemy.exc import IntegrityError
from flask_login import current_user

# --- Route Handlers ---

@bp.route('/', methods=['GET'])
@login_required
@superadmin_required
def list_users():
    """List all users."""
    users = User.query.all()
    # USER_ROLES is passed to template for human-readable names
    return render_template('user/user_list.html', users=users, user_roles=USER_ROLES)


@bp.route('/edit', defaults={'user_id': None}, methods=['GET', 'POST'])
@bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@superadmin_required
def edit_user(user_id):
    """Create or update a user."""
    
    if user_id:
        user = db.get_or_404(User, user_id)
        
        # Prevent editing SuperAdmins
        if user.role == 0:
            flash("Cannot edit a SuperAdmin.", 'error')
            return redirect(url_for('user.list_users'))

        action_text = 'Edit'
        # Optional: Prevent SuperAdmin from editing other SuperAdmins
        if user.role == 0 and user.id != current_user.id:
            flash("Cannot edit another SuperAdmin.", 'error')
            return redirect(url_for('user.list_users'))

    else:
        user = User(role=2) # Default to Moderator role
        action_text = 'Create'
        
    form = UserForm(obj=user)
    
    # Pass the object to the form for unique validation checks
    form.original_user = user 
    
    # Role choices are already filtered in UserForm (r > 0)

    if form.validate_on_submit():
        # Populate common fields
        form.populate_obj(user)

        # Handle Password: only update if the password field is populated
        if form.password.data:
            user.set_password(form.password.data) # uses set_password from models.py

        try:
            db.session.add(user)
            db.session.commit()
            flash(f'User "{user.username}" saved successfully.', 'success')
            return redirect(url_for('user.list_users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Failed to save user: {e}', 'error')

    return render_template('user/user_edit.html', form=form, user=user, action_text=action_text)


@bp.route('/delete/<int:user_id>', methods=['POST'])
@login_required
@superadmin_required
def delete_user(user_id):
    """Delete a user."""
    user = db.get_or_404(User, user_id)
    
    # Prevent deleting SuperAdmins
    if user.role == 0:
        flash("Cannot delete a SuperAdmin.", 'error')
        return redirect(url_for('user.list_users'))
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'User "{user.username}" deleted successfully.', 'success')
    except Exception:
        db.session.rollback()
        flash(f'Failed to delete user.', 'error')

    return redirect(url_for('user.list_users'))