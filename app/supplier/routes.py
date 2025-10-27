# app/supplier/routes.py

from flask import render_template, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models import Supplier, SUPPLIER_TYPES
from app.forms import SupplierForm
from app.supplier import bp 
from app.utils import admin_or_superadmin_required, admin_required
from sqlalchemy.exc import IntegrityError

# --- CRUD Handlers ---

@bp.route('/', methods=['GET'])
@login_required
@admin_or_superadmin_required
def list_suppliers():
    """List all suppliers (Wholesalers and Factories)."""
    suppliers = Supplier.query.all()
    
    return render_template('supplier/supplier_list.html', 
                           suppliers=suppliers, 
                           supplier_types=SUPPLIER_TYPES,
                           title='Supplier Management')

@bp.route('/edit', defaults={'supplier_id': None}, methods=['GET', 'POST'])
@bp.route('/edit/<int:supplier_id>', methods=['GET', 'POST'])
@login_required
@admin_required # Only Admins can modify suppliers
def edit_supplier(supplier_id):
    """Create or update a supplier."""
    
    supplier = db.get_or_404(Supplier, supplier_id) if supplier_id else Supplier()
    action_text = 'Edit' if supplier_id else 'Create'
        
    form = SupplierForm(obj=supplier)

    if form.validate_on_submit():
        try:
            if supplier_id: # Edit
                form.populate_obj(supplier)
                flash(f'Supplier "{supplier.name}" updated successfully.', 'success')
            else: # Create
                form.populate_obj(supplier)
                db.session.add(supplier)
                flash(f'Supplier "{supplier.name}" created successfully.', 'success')
            
            db.session.commit()
            return redirect(url_for('supplier.list_suppliers'))
        
        except IntegrityError:
            db.session.rollback() 
            flash(f"Failed to save supplier. The name '{form.name.data}' is likely already taken.", 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'An unexpected error occurred: {e}', 'error')

    return render_template('supplier/supplier_edit.html', 
                           form=form, 
                           supplier=supplier, 
                           action_text=action_text)

# Note: A delete route should also be implemented, similar to the user delete route.