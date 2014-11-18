from flask import request, jsonify, g, url_for, Blueprint

from app.api import db, auth
from app.api.helpers import *
from app.api.cuisine_types.model import *


mod = Blueprint('cuisine_types', __name__, url_prefix='/api/cuisine_types')