# app/supplier/__init__.py

from flask import Blueprint

bp = Blueprint('supplier', __name__, url_prefix='/suppliers')

from . import routes