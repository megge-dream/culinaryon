from flask import request, jsonify, g, url_for, Blueprint
from flask.ext.login import login_required
from sqlalchemy.sql import label, func

from app.api import db, auto
from app.api.constants import OK, BAD_REQUEST
from app.api.helpers import *
from app.api.dictionary.model import Dictionary
from app.decorators import admin_required


mod = Blueprint('dictionary_v2', __name__, url_prefix='/api_v2/dictionary')


@auto.doc()
@mod.route('/', methods=['POST'])
@login_required
@admin_required
def new_dictionary():
    """
    Add new dictionary. List of parameters in json request:
            title (required)
            description (optional)
    Example of request:
            {"title":"good", "description":"smth smart"}
    :return: json with parameters:
            error_code - server response_code
            result - information about created dictionary
    """
    title = request.json.get('title')
    description = request.json.get('description')
    lang = request.args.get('lang', type=unicode, default=u'en')
    if title is None or description is None:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # missing arguments
    dictionary = Dictionary(title=title, description=description)
    db.session.add(dictionary)
    db.session.commit()
    information = response_builder(dictionary, Dictionary, lang)
    return jsonify({'error_code': OK, 'result': information}), 201


@auto.doc()
@mod.route('/<int:id>', methods=['PUT'])
@login_required
@admin_required
def update_dictionary(id):
    """
    Update exists dictionary. List of parameters in json request:
            title (optional)
            description (optional)
    Example of request:
            {"title":"good"}
    :param id: dictionary id
    :return: json with parameters:
            error_code - server response_code
            result - information about updated dictionary
    """
    dictionary = Dictionary.query.get(id)
    if not dictionary:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200
    if request.json.get('title'):
        dictionary.title = request.json.get('title')
    if request.json.get('description'):
        dictionary.description = request.json.get('description')
    db.session.commit()
    dictionary = Dictionary.query.get(id)
    information = response_builder(dictionary, Dictionary)
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['GET'])
def get_dictionary(id):
    """
    Get information about dictionary.
    :param id: dictionary id
    :return: json with parameters:
            error_code - server response_code
            result - information about dictionary
    """
    dictionary = Dictionary.query.get(id)
    lang = request.args.get('lang', type=unicode, default=u'en')
    if not dictionary:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # dictionary with `id` isn't exist
    information = response_builder(dictionary, Dictionary, lang)
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/', methods=['GET'])
def get_all_dictionares():
    """
    Get information about all exist dictionaries.
    :return: json with parameters:
            error_code - server response_code
            result - information about dictionaries
    """
    dic = db.session.query(func.substr(Dictionary.title, 1, 1)).group_by(func.substr(Dictionary.title, 1, 1)).all()
    result = {}
    lang = request.args.get('lang', type=unicode, default=u'en')
    for letter_arr in dic:
        letter = letter_arr[0]
        results_for_letter = []
        for dictionary in Dictionary.query.all():
            if dictionary.title[0] == letter:
                information = response_builder(dictionary, Dictionary, lang)
                results_for_letter.append(information)
        result.update({letter: results_for_letter})
    return jsonify({'error_code': OK, 'result': result}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_dictionary(id):
    """
    Delete dictionary.
    :param id: dictionary id
    :return: json with parameters:
            error_code - server response_code
    """
    dictionary = Dictionary.query.get(id)
    if not dictionary:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # dictionary with `id` isn't exist
    db.session.delete(dictionary)
    db.session.commit()
    return jsonify({'error_code': OK}), 200