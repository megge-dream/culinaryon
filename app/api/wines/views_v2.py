from flask import request, jsonify, g, url_for, Blueprint
from flask.ext.login import login_required

from app.api import db, auto
from app.api.constants import BAD_REQUEST, OK
from app.api.helpers import *
from app.api.wines.model import Wine
from app.decorators import admin_required


mod = Blueprint('wines_v2', __name__, url_prefix='/api_v2/wines')


@auto.doc()
@mod.route('/', methods=['POST'])
@login_required
@admin_required
def new_wine():
    """
    Add new wine. List of parameters in json request:
            title (required)
    Example of request:
            {"title":"good"}
    :return: json with parameters:
            error_code - server response_code
            result - information about created wine
    """
    title = request.json.get('title')
    if title is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # missing arguments
    wine = Wine(title=title)
    db.session.add(wine)
    db.session.commit()
    information = response_builder(wine, Wine)
    return jsonify({'error_code': OK, 'result': information}), 201


@auto.doc()
@mod.route('/<int:id>', methods=['PUT'])
@login_required
@admin_required
def update_wine(id):
    """
    Update exists wine. List of parameters in json request:
            title (optional)
    Example of request:
            {"title":"good"}
    :param id: wine id
    :return: json with parameters:
            error_code - server response_code
            result - information about updated wine
    """
    wine = Wine.query.get(id)
    if not wine:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200
    if request.json.get('title'):
        wine.title = request.json.get('title')
    db.session.commit()
    wine = Wine.query.get(id)
    information = response_builder(wine, Wine)
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['GET'])
def get_wine(id):
    """
    Get information about wine.
    :param id: wine id
    :return: json with parameters:
            error_code - server response_code
            result - information about wine
    """
    wine = Wine.query.get(id)
    if not wine:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # wine with `id` isn't exist
    information = response_builder(wine, Wine)
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/', methods=['GET'])
def get_all_wines():
    """
    Get information about all exist wines.
    :return: json with parameters:
            error_code - server response_code
            result - information about wines
    """
    wines = []
    for wine in Wine.query.all():
        information = response_builder(wine, Wine)
        wines.append(information)
    return jsonify({'error_code': OK, 'result': wines}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_wine(id):
    """
    Delete wine.
    :param id: wine id
    :return: json with parameters:
            error_code - server response_code
    """
    wine = Wine.query.get(id)
    if not wine:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # wine with `id` isn't exist
    db.session.delete(wine)
    db.session.commit()
    return jsonify({'error_code': OK}), 200