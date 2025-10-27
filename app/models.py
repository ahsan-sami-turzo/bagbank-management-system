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

    # Foreign Key to Supplier (NEW LINK)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))

    # Relationships (for easy access to attribute names)
    style = db.relationship('Style')
    category = db.relationship('Category')
    brand = db.relationship('Brand')
    material = db.relationship('Material')
    
    # Variants relationship
    variants = db.relationship('ProductVariant', backref='product', lazy='dynamic', cascade="all, delete-orphan")

class ProductVariant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Link to parent product
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    
    # Link to color attribute
    color_id = db.Column(db.Integer, db.ForeignKey('color.id'), nullable=False)
    
    # Inventory/SKU data
    sku = db.Column(db.String(100), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)

    color = db.relationship('Color')
    
    # Constraint: A product can only have one variant per color
    __table_args__ = (db.UniqueConstraint('product_id', 'color_id', name='_product_color_uc'),)