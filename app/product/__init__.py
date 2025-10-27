# app/product/__init__.py

from flask import Blueprint

bp = Blueprint('product', __name__, template_folder='templates')

# This single line handles all route registration in routes.py
from . import routes 

