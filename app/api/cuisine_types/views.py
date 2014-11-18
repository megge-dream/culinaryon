from flask import request, jsonify, g, url_for, Blueprint

from app.api.helpers import *
from app.api.cuisine_types.model import *


mod = Blueprint('cuisine_types', __name__, url_prefix='/api/cuisine_types')


# {"title":"good"}
@mod.route('/', methods=['POST'])
def new_cuisine_type():
    title = request.json.get('title')
    if title is None:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # missing arguments
    cuisine_type = CuisineType(title=title)
    db.session.add(cuisine_type)
    db.session.commit()
    information = response_builder(cuisine_type, CuisineType)
    return jsonify({'error_code': 201, 'result': information}), 201


@mod.route('/<int:id>', methods=['PUT'])
def update_cuisine_type(id):
    cuisine_type = CuisineType.query.get(id)
    if not cuisine_type:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200
    if request.json.get('title'):
        cuisine_type.title = request.json.get('title')
    db.session.commit()
    cuisine_type = CuisineType.query.get(id)
    information = response_builder(cuisine_type, CuisineType)
    return jsonify({'error_code': 200, 'result': information}), 200


@mod.route('/<int:id>', methods=['GET'])
def get_cuisine_type(id):
    cuisine_type = CuisineType.query.get(id)
    if not cuisine_type:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # cuisine_type with `id` isn't exist
    information = response_builder(cuisine_type, CuisineType)
    return jsonify({'error_code': 200, 'result': information}), 200


@mod.route('/', methods=['GET'])
def get_all_cuisine_types():
    cuisine_types = []
    for cuisine_type in CuisineType.query.all():
        information = response_builder(cuisine_type, CuisineType)
        cuisine_types.append(information)
    return jsonify({'error_code': 200, 'result': cuisine_types}), 200


@mod.route('/<int:id>', methods=['DELETE'])
def delete_cuisine_type(id):
    cuisine_type = CuisineType.query.get(id)
    if not cuisine_type:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # cuisine_type with `id` isn't exist
    db.session.delete(cuisine_type)
    db.session.commit()
    return jsonify({'error_code': 200}), 200