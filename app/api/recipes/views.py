from flask import request, jsonify, g, url_for, Blueprint

from app.api import db, auth
from app.api.helpers import *
from app.api.recipes.model import Recipe


mod = Blueprint('recipes', __name__, url_prefix='/api/recipes')