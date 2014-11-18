from flask import request, jsonify, g, url_for, Blueprint

from app.api import db, auth
from app.api.helpers import *
from app.api.schools.model import *


mod = Blueprint('schools', __name__, url_prefix='/api/schools')