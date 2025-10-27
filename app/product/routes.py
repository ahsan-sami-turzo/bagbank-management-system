# app/product/routes.py (Final Revision for Modularity and Stability)

from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from functools import wraps
from app import db
from app.models import Product, Style, Category, Brand, Material, Supplier, Color, ProductImage
from app.forms import CategoricalForm, BrandForm, ColorForm, ProductForm
from app.product import bp 
from app.utils import admin_or_superadmin_required, admin_required
from app.file_utils import save_and_process_image, slugify
from sqlalchemy.exc import IntegrityError

# --- Configuration: Define Models and Forms ---
MODELS = [
    (Style, 'styles', CategoricalForm),
    (Category, 'categories', CategoricalForm),
    (Brand, 'brands', BrandForm),
    (Material, 'materials', CategoricalForm),
    (Color, 'colors', ColorForm),
]

# --- Generic Route Handler Creator ---
def create_route_handlers(model, route_name, form_class):
    """Creates the view functions (list and edit) using closures."""

    # 1. READ/LIST View Function
    def list_items_view():
        items = model.query.all()
        return render_template(f'product/categorical_list.html', 
                               items=items, 
                               name=route_name, 
                               title=f'{route_name.title()} Management')
    
    # 2. CREATE/UPDATE View Function
    def edit_item_view(item_id=None):
        item = db.get_or_404(model, item_id) if item_id else None
        form = form_class(obj=item)
        
        # Determine which template to use: dedicated for colors, generic for others
        template_name = 'product/color_edit.html' if route_name == 'colors' else 'product/categorical_edit.html'
        
        if form.validate_on_submit():            
            try:
                if item: # Edit existing item
                    form.populate_obj(item)
                    flash(f'{route_name.title()} updated successfully.', 'success')
                else: # Create new item
                    new_item = model()
                    form.populate_obj(new_item)
                    db.session.add(new_item)
                    flash(f'{route_name.title()} created successfully.', 'success')
                
                # Attempt the commit
                db.session.commit() 
                return redirect(url_for(f'product.list_{route_name}'))
            
            except IntegrityError:
                # Catch database error (usually unique constraint violation)
                db.session.rollback() 
                
                # Flash error message to the user
                error_message = f"Failed to save {route_name[:-1].title()}. The name '{form.name.data}' is likely already taken."
                flash(error_message, 'error') 
                
                # If an error occurred, fall through to re-render the template
                pass
            
            return redirect(url_for(f'product.list_{route_name}'))
        
        return render_template(template_name, 
                               form=form, 
                               item=item, 
                               name=route_name, 
                               title=f'Edit {route_name.title()}')
    
    return list_items_view, edit_item_view


# --- Route Registration (Runs on Module Import) ---
for model, route_name, form_class in MODELS:
    list_func, edit_func = create_route_handlers(model, route_name, form_class)

    # 1. Apply decorators manually:
    
    # LIST VIEW: Requires Admin OR SuperAdmin to see the data.
    list_func_wrapped = login_required(list_func)
    list_func_wrapped = admin_or_superadmin_required(list_func_wrapped) 

    # EDIT VIEW: Requires ONLY Admin (Role 1) to perform modifications.
    edit_func_wrapped = login_required(edit_func)
    edit_func_wrapped = admin_required(edit_func_wrapped) 
    
    # 2. Register the URL rules... (remains the same)
    bp.add_url_rule(f'/{route_name}', 
                    endpoint=f'list_{route_name}',
                    view_func=list_func_wrapped)
    
    bp.add_url_rule(f'/{route_name}/edit', 
                    defaults={'item_id': None}, 
                    methods=['GET', 'POST'],
                    endpoint=f'edit_{route_name}_create',
                    view_func=edit_func_wrapped)
    
    bp.add_url_rule(f'/{route_name}/edit/<int:item_id>', 
                    methods=['GET', 'POST'],
                    endpoint=f'edit_{route_name}',
                    view_func=edit_func_wrapped)
    

# --- Helper function to populate FK choices ---
def populate_product_choices(form):
    """Dynamically loads choices for SelectFields in ProductForm."""
    form.style_id.choices = [(s.id, s.name) for s in Style.query.all()]
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    form.brand_id.choices = [(b.id, b.name) for b in Brand.query.all()]
    form.material_id.choices = [(m.id, m.name) for m in Material.query.all()]
    form.supplier_id.choices = [(s.id, f"{s.name} ({s.get_type_name()})") for s in Supplier.query.all()]
    form.colors.choices = [(c.id, c.name) for c in Color.query.order_by(Color.name).all()]

# --- Product Routes ---
@bp.route('/', methods=['GET'])
@login_required
@admin_or_superadmin_required
def list_products():
    """Display the list of main products."""
    products = Product.query.order_by(Product.name).all()
    return render_template('product/product_list.html', products=products, title='Product Inventory')


@bp.route('/edit', defaults={'product_id': None}, methods=['GET', 'POST'])
@bp.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_or_superadmin_required
def edit_product(product_id):
    """Create or update core product details, including base and additional photos."""
    
    product = db.get_or_404(Product, product_id) if product_id else Product()
    action_text = 'Edit' if product_id else 'Create'
    form = ProductForm(obj=product)
    
    # CRITICAL: Populate dropdown choices before validation
    populate_product_choices(form)

    if form.validate_on_submit():
        try:
            # 1. Save Core Details & Flush
            # Populate standard fields (name, style, colors, etc.)
            form.populate_obj(product)
            db.session.add(product)
            # Flush session to get product.id for image paths before final commit
            db.session.flush() 
            
            # 2. Prepare for Image Handling
            product_slug = slugify(product.name)
            
            # --- 3. Handle Base Photo (Required for New Product, Optional for Edit) ---
            base_photo_file = form.base_photo.data
            
            # Conditional Validation Check: Base photo required if product is new and no file is submitted
            if not product_id and not base_photo_file:
                 flash("A Base Photo is required when creating a new product.", 'error')
                 # If validation fails here, we must roll back the flushed session state
                 db.session.rollback() 
                 return render_template('product/product_edit.html', form=form, product=product, action_text=action_text)

            if base_photo_file:
                relative_path = save_and_process_image(base_photo_file, product_slug, 'base')
                
                if relative_path:
                    # Find or create the base photo record
                    base_image = ProductImage.query.filter_by(product_id=product.id, type='base').first()
                    
                    if not base_image:
                        base_image = ProductImage(product_id=product.id, type='base')
                        db.session.add(base_image)
                        
                    base_image.file_path = relative_path
                    flash("Base photo uploaded and processed.", 'success')
                else:
                    flash("Failed to process Base Photo. Check file type and content.", 'error')


            # --- 4. Handle Additional Photos ---
            for file_storage in form.additional_photos.data:
                # Check if file_storage is an actual file and not an empty field
                if file_storage and file_storage.filename:
                    # Process and save the file
                    relative_path = save_and_process_image(file_storage, product_slug, 'additional')
                    
                    if relative_path:
                        # Create a new record for each additional photo
                        image = ProductImage(
                            product_id=product.id, 
                            type='additional', 
                            file_path=relative_path
                        )
                        db.session.add(image)
                        
            
            # 5. Final Commit
            db.session.commit()
            flash(f'Product "{product.name}" and images saved successfully.', 'success')
            
            # Redirect to the edit page to manage images/variants further
            return redirect(url_for('product.edit_product', product_id=product.id))
            
        except IntegrityError:
            db.session.rollback()
            flash(f"Failed to save product. Name '{form.name.data}' may already be taken.", 'error')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error during product save: {e}")
            flash(f'An unexpected error occurred: {e}', 'error')

    # Pass existing images to the template for display
    base_image = ProductImage.query.filter_by(product_id=product_id, type='base').first() if product_id else None
    additional_images = ProductImage.query.filter_by(product_id=product_id, type='additional').all() if product_id else []
    
    return render_template('product/product_edit.html', 
                           form=form, 
                           product=product, 
                           action_text=action_text,
                           base_image=base_image,
                           additional_images=additional_images)

# NOTE: You will also need a delete_product route.