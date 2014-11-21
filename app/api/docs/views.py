from flask import Blueprint
from app.api import auto

mod = Blueprint('docs', __name__, url_prefix='/docs')

@mod.route("/")
def docs():
    return auto.html()
