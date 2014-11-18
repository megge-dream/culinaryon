from flask import request, jsonify, g, url_for, Blueprint

from app.api import db, auth
from app.api.helpers import *
from app.api.dictionary.model import Dictionary


mod = Blueprint('dictionary', __name__, url_prefix='/api/dictionary')