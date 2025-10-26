from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User, USER_ROLES

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