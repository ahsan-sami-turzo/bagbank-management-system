# app/main/__init__.py (FIXED)

from flask import Blueprint

# 1. Define the Blueprint instance
bp = Blueprint('main', __name__, template_folder='templates')

# 2. Import the routes (relative import ensures the 'bp' is defined first)
from . import routes