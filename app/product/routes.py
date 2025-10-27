# app/product/routes.py (Final Revision for Modularity and Stability)

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from functools import wraps
from app import db
from app.models import Style, Category, Brand
from app.forms import CategoricalForm, BrandForm
from app.product import bp # Use the Blueprint instance
from app.utils import admin_or_superadmin_required 

# --- Configuration: Define Models and Forms ---
MODELS = [
    (Style, 'styles', CategoricalForm),
    (Category, 'categories', CategoricalForm),
    (Brand, 'brands', BrandForm),
]

# --- Generic Route Handler Creator ---
def create_route_handlers(model, route_name, form_class):
    """Creates the view functions (list and edit) using closures."""

    # 1. READ/LIST View Function
    def list_items_view():
        items = model.query.all()
        return render_template(f'product/{route_name}_list.html', 
                               items=items, 
                               name=route_name, 
                               title=f'{route_name.title()} Management')
    
    # 2. CREATE/UPDATE View Function
    def edit_item_view(item_id=None):
        item = db.get_or_404(model, item_id) if item_id else None
        form = form_class(obj=item)
        # ... (rest of your form submission logic) ...
        if form.validate_on_submit():
            # ... commit logic ...
            return redirect(url_for(f'product.list_{route_name}'))
        
        return render_template('product/categorical_edit.html', 
                               form=form, 
                               item=item, 
                               name=route_name, 
                               title=f'Edit {route_name.title()}')
    
    return list_items_view, edit_item_view


# --- Route Registration (Runs on Module Import) ---
for model, route_name, form_class in MODELS:
    list_func, edit_func = create_route_handlers(model, route_name, form_class)

    # 1. Apply decorators manually
    list_func_wrapped = login_required(list_func)
    # list_func_wrapped = admin_or_superadmin_required(list_func_wrapped) 

    edit_func_wrapped = login_required(edit_func)
    # edit_func_wrapped = admin_or_superadmin_required(edit_func_wrapped)

    # 2. Register the URL rules using the blueprint instance's method
    # CRITICAL: We rely on the endpoint name to be unique for each model type.
    bp.add_url_rule(f'/{route_name}', 
                    endpoint=f'list_{route_name}', # e.g., 'list_styles'
                    view_func=list_func_wrapped)
    
    # Edit/Create route handles both the ID and no ID case
    bp.add_url_rule(f'/{route_name}/edit', 
                    defaults={'item_id': None}, 
                    methods=['GET', 'POST'],
                    endpoint=f'edit_{route_name}_create', # e.g., 'edit_styles_create'
                    view_func=edit_func_wrapped)
    
    bp.add_url_rule(f'/{route_name}/edit/<int:item_id>', 
                    methods=['GET', 'POST'],
                    endpoint=f'edit_{route_name}', # e.g., 'edit_styles'
                    view_func=edit_func_wrapped)

# DELETE the empty register_product_routes function definition.