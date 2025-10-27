# app/user/__init__.py

from flask import Blueprint

bp = Blueprint('user', __name__, url_prefix='/users')

from . import routes