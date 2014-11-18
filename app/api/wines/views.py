from flask import request, jsonify, g, url_for, Blueprint

from app.api import db, auth
from app.api.helpers import *
from app.api.wines.model import Wine


mod = Blueprint('wines', __name__, url_prefix='/api/wines')


# {"title":"good"}
@mod.route('/', methods=['POST'])
def new_wine():
    title = request.json.get('title')
    if title is None:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # missing arguments
    wine = Wine(title=title)
    db.session.add(wine)
    db.session.commit()
    information = response_builder(wine, Wine)
    return jsonify({'error_code': 201, 'result': information}), 201


@mod.route('/<int:id>', methods=['PUT'])
def update_wine(id):
    wine = Wine.query.get(id)
    if not wine:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200
    if request.json.get('title'):
        wine.title = request.json.get('title')
    db.session.commit()
    wine = Wine.query.get(id)
    information = response_builder(wine, Wine)
    return jsonify({'error_code': 200, 'result': information}), 200


@mod.route('/<int:id>', methods=['GET'])
def get_wine(id):
    wine = Wine.query.get(id)
    if not wine:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # wine with `id` isn't exist
    information = response_builder(wine, Wine)
    return jsonify({'error_code': 200, 'result': information}), 200


@mod.route('/', methods=['GET'])
def get_all_wines():
    wines = []
    for wine in Wine.query.all():
        information = response_builder(wine, Wine)
        wine.append(information)
    return jsonify({'error_code': 200, 'result': wines}), 200


@mod.route('/<int:id>', methods=['DELETE'])
def delete_wine(id):
    wine = Wine.query.get(id)
    if not wine:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # wine with `id` isn't exist
    db.session.delete(wine)
    db.session.commit()
    return jsonify({'error_code': 200}), 200