# app/product/__init__.py

from flask import Blueprint

#  bp = Blueprint('product', __name__, template_folder='templates')
bp = Blueprint('product', __name__)

from . import routes 

