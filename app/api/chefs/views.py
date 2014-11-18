from flask import request, jsonify, g, url_for, Blueprint, redirect, Flask

from app.api import db, auth
from app.api.helpers import *
from app.api.chefs.model import *

mod = Blueprint('chefs', __name__, url_prefix='/api/chefs')