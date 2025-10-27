# app/models.py

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

    def get_role_name(self):
        """Return human-readable role name."""
        # FIX: Use the USER_ROLES dictionary for reliable mapping
        return USER_ROLES.get(self.role, "User") 

    def is_superadmin(self):
        # FIX: Check against integer 0
        return self.role == 0 

    def is_admin_or_superadmin(self):
        # FIX: Check against integers 0 or 1
        return self.role in [0, 1]


class Style(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class Brand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    is_own_brand = db.Column(db.Boolean, default=False)

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

class Color(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    hex_code = db.Column(db.String(7), unique=True, nullable=False)


# Define Supplier Types (1=Wholesaler, 2=Factory)
SUPPLIER_TYPES = {1: 'Wholesaler', 2: 'Factory'} 

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Type: 1=Wholesaler, 2=Factory
    supplier_type = db.Column(db.Integer, default=1, nullable=False)
    
    # Mandatory Fields
    name = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    # Optional Contact/Location Fields
    address = db.Column(db.String(255))
    contact_person = db.Column(db.String(100))
    website = db.Column(db.String(255))
    facebook_page = db.Column(db.String(255))
    whatsapp_number = db.Column(db.String(20))

    # Optional Financial Fields
    mobile_banking_number = db.Column(db.String(50))
    bank_account_number = db.Column(db.String(50))

    # Products supplied by this entity
    products = db.relationship('Product', backref='supplier', lazy='dynamic')
    
    def get_type_name(self):
        return SUPPLIER_TYPES.get(self.supplier_type, 'Unknown')


# --- Product/Variant Structure  ---

# --- Association Table ---
product_color_association = db.Table('product_color_association',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
    db.Column('color_id', db.Integer, db.ForeignKey('color.id'), primary_key=True)
)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    facebook_post = db.Column(db.String(255))
    youtube_video = db.Column(db.String(255))
    keywords = db.Column(db.String(255))

    # Foreign Keys to Product Attributes
    style_id = db.Column(db.Integer, db.ForeignKey('style.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    brand_id = db.Column(db.Integer, db.ForeignKey('brand.id'))
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'))

    # Foreign Key to Supplier
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))

    # Relationships (for easy access to attribute names)
    style = db.relationship('Style')
    category = db.relationship('Category')
    brand = db.relationship('Brand')
    material = db.relationship('Material')
    
    # Many-to-Many Relationship with Color (as discussed)
    colors = db.relationship('Color', secondary=product_color_association,
                             backref=db.backref('products', lazy='dynamic'))

    # Images relationship (NEW)
    images = db.relationship('ProductImage', backref='product', lazy='dynamic', cascade="all, delete-orphan")


# --- ProductImage Model ---
class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    
    # Type: 'base', 'additional', or specific color type like 'color_maroon' (optional future use)
    type = db.Column(db.String(50), nullable=False) 
    
    # Path relative to the UPLOAD_FOLDER
    file_path = db.Column(db.String(255), nullable=False)
    
    # Optional: Link to a specific color ID if this is a color-specific photo
    color_id = db.Column(db.Integer, db.ForeignKey('color.id'), nullable=True) 

    color = db.relationship('Color')
    
    def __repr__(self):
        return f"<Image {self.file_path}>"