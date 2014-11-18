from flask import request, jsonify, g, url_for, Blueprint

from app.api import db, auth
from app.api.helpers import *
from app.api.dictionary.model import Dictionary


mod = Blueprint('dictionary', __name__, url_prefix='/api/dictionary')


# {"title":"good"}
@mod.route('/', methods=['POST'])
def new_dictionary():
    title = request.json.get('title')
    description = request.json.get('description')
    if title is None or description is None:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # missing arguments
    dictionary = Dictionary(title=title, description=description)
    db.session.add(dictionary)
    db.session.commit()
    information = response_builder(dictionary, Dictionary)
    return jsonify({'error_code': 201, 'result': information}), 201


@mod.route('/<int:id>', methods=['PUT'])
def update_dictionary(id):
    dictionary = Dictionary.query.get(id)
    if not dictionary:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200
    if request.json.get('title'):
        dictionary.title = request.json.get('title')
    if request.json.get('description'):
        dictionary.description = request.json.get('description')
    db.session.commit()
    dictionary = Dictionary.query.get(id)
    information = response_builder(dictionary, Dictionary)
    return jsonify({'error_code': 200, 'result': information}), 200


@mod.route('/<int:id>', methods=['GET'])
def get_dictionary(id):
    dictionary = Dictionary.query.get(id)
    if not dictionary:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # dictionary with `id` isn't exist
    information = response_builder(dictionary, Dictionary)
    return jsonify({'error_code': 200, 'result': information}), 200


@mod.route('/', methods=['GET'])
def get_all_dictionares():
    dictionares = []
    for dictionary in Dictionary.query.all():
        information = response_builder(dictionary, Dictionary)
        dictionary.append(information)
    return jsonify({'error_code': 200, 'result': dictionares}), 200


@mod.route('/<int:id>', methods=['DELETE'])
def delete_dictionary(id):
    dictionary = Dictionary.query.get(id)
    if not dictionary:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # dictionary with `id` isn't exist
    db.session.delete(dictionary)
    db.session.commit()
    return jsonify({'error_code': 200}), 200