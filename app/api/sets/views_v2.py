# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify
from app.api import auto
from app.api.constants import BAD_REQUEST, OK
from app.api.helpers import response_builder
from app.api.sets.model import Set


mod = Blueprint('sets', __name__, url_prefix='/api_v2/sets')

@auto.doc()
@mod.route('/<int:id>', methods=['GET'])
def get_set(id):
    """
    Get information about set.
    :param id: set id
    :return: json with parameters:
            error_code - server response_code
            result - information about category
    """
    set = Set.query.get(id)
    if not set:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # set with `id` isn't exist
    information = response_builder(set, Set)
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/', methods=['GET'])
def get_all_sets():
    """
    Get information about all exist sets.
    :return: json with parameters:
            error_code - server response_code
            result - information about sets
    """
    sets = []
    for set in Set.query.all():
        information = response_builder(set, Set)
        sets.append(information)
    ids = []
    sets_ids = Set.query.all()
    for set_id in sets_ids:
        ids.append(set_id.id)
    return jsonify({'error_code': OK, 'result': sets, 'ids': ids}), 200
