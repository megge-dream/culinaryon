from flask import request, jsonify, g, url_for, Blueprint

from app.api import db, auth
from app.api.helpers import *
from app.api.wines.model import Wine


mod = Blueprint('wines', __name__, url_prefix='/api/wines')