from flask import request, jsonify, g, url_for, Blueprint
from flask.ext.login import login_required
from app.api import auto
from app.api.constants import OK, BAD_REQUEST

from app.api.helpers import *
from app.api.cuisine_types.model import *
from app.decorators import admin_required


mod = Blueprint('cuisine_types_v2', __name__, url_prefix='/api_v2/cuisine_types')


@auto.doc()
@mod.route('/', methods=['POST'])
@login_required
@admin_required
def new_cuisine_type():
    """
    Add new cuisine type. List of parameters in json request:
            title (required)
    Example of request:
            {"title":"good"}
    :return: json with parameters:
            error_code - server response_code
            result - information about created cuisine type
    """
    title = request.json.get('title')
    if title is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # missing arguments
    cuisine_type = CuisineType(title=title)
    db.session.add(cuisine_type)
    db.session.commit()
    information = response_builder(cuisine_type, CuisineType)
    return jsonify({'error_code': OK, 'result': information}), 201


@auto.doc()
@mod.route('/<int:id>', methods=['PUT'])
@login_required
@admin_required
def update_cuisine_type(id):
    """
    Update exists cuisine type. List of parameters in json request:
            title (optional)
    Example of request:
            {"title":"good"}
    :param id: cuisine type id
    :return: json with parameters:
            error_code - server response_code
            result - information about updated cuisine type
    """
    cuisine_type = CuisineType.query.get(id)
    if not cuisine_type:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200
    if request.json.get('title'):
        cuisine_type.title = request.json.get('title')
    db.session.commit()
    cuisine_type = CuisineType.query.get(id)
    information = response_builder(cuisine_type, CuisineType)
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['GET'])
def get_cuisine_type(id):
    """
    Get information about cuisine type.
    :param id: cuisine type id
    :return: json with parameters:
            error_code - server response_code
            result - information about cuisine type
    """
    cuisine_type = CuisineType.query.get(id)
    if not cuisine_type:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # cuisine_type with `id` isn't exist
    information = response_builder(cuisine_type, CuisineType)
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/', methods=['GET'])
def get_all_cuisine_types():
    """
    Get information about all exist cuisine types.
    :return: json with parameters:
            error_code - server response_code
            result - information about cuisine types
    """
    cuisine_types = []
    for cuisine_type in CuisineType.query.all():
        information = response_builder(cuisine_type, CuisineType)
        cuisine_types.append(information)
    return jsonify({'error_code': OK, 'result': cuisine_types}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_cuisine_type(id):
    """
    Delete cuisine type.
    :param id: cuisine type id
    :return: json with parameters:
            error_code - server response_code
    """
    cuisine_type = CuisineType.query.get(id)
    if not cuisine_type:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # cuisine_type with `id` isn't exist
    db.session.delete(cuisine_type)
    db.session.commit()
    return jsonify({'error_code': OK}), 200