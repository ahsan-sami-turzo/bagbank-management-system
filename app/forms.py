# app/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User, USER_ROLES, SUPPLIER_TYPES

# --- Login Form ---
class LoginForm(FlaskForm):
    # The user can log in with either username or email
    username = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')

# --- User CRUD Form ---
class UserForm(FlaskForm):
    # DataRequired ensures the field isn't empty on submission
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone Number', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=80)])
    
    # We use optional=True to allow editing a user without changing the password
    password = PasswordField('New Password', validators=[EqualTo('confirm_password')])
    confirm_password = PasswordField('Confirm New Password')
    
    # SuperAdmins can only create/edit Admin or Moderator roles (excluding SuperAdmin itself)
    # Note: We must convert the dictionary to a list of tuples for SelectField
    role = SelectField('Role', coerce=int, validators=[DataRequired()], 
                       choices=[(r, name) for r, name in USER_ROLES.items() if r > 0])
    
    # This field will be handled separately (file upload) but we include it for structure
    # photo_file = FileField('User Photo', validators=[FileAllowed(['jpg', 'png'])])
    
    submit = SubmitField('Save User')

    # Custom validation methods to ensure unique fields when adding/editing
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            # Check if this user is the one being edited (if applicable)
            if not hasattr(self, 'original_user') or self.original_user.username != username.data:
                raise ValidationError('That username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
             # Check if this user is the one being edited (if applicable)
            if not hasattr(self, 'original_user') or self.original_user.email != email.data:
                raise ValidationError('That email is already in use. Please choose a different one.')
            

# --- Category Form ---
class CategoricalForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Save')

# --- Brand Form ---
class BrandForm(CategoricalForm):
    # Brand is slightly different because of the boolean field
    is_own_brand = BooleanField('Is Own Brand?')
    # No need to redefine name or submit

# --- Color Form ---
class ColorForm(FlaskForm):
    # Name is still required
    name = StringField('Color Name', validators=[DataRequired(), Length(max=100)])
    
    # Hex code field (e.g., #FF00FF)
    hex_code = StringField('Hex Code', validators=[
        DataRequired(), 
        Length(min=7, max=7, message='Hex code must be 7 characters (e.g., #1A2B3C)'),
    ])
    submit = SubmitField('Save')

# --- Supplier CRUD Form ---
class SupplierForm(FlaskForm):
    # Select field for type
    supplier_type = SelectField('Type', coerce=int, validators=[DataRequired()], 
                                choices=[(r, name) for r, name in SUPPLIER_TYPES.items()])
    
    # Mandatory Fields
    name = StringField('Name', validators=[DataRequired(), Length(max=150)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=20)])

    # Optional Fields
    address = StringField('Address', validators=[Length(max=255)])
    contact_person = StringField('Contact Person', validators=[Length(max=100)])
    website = StringField('Website/Link', validators=[Length(max=255)])
    facebook_page = StringField('Facebook Page', validators=[Length(max=255)])
    whatsapp_number = StringField('WhatsApp Number', validators=[Length(max=20)])
    mobile_banking_number = StringField('Mobile Banking Number', validators=[Length(max=50)])
    bank_account_number = StringField('Bank Account Number', validators=[Length(max=50)])
    
    submit = SubmitField('Save Supplier')