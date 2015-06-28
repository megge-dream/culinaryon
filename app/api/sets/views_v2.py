# -*- coding: utf-8 -*-
from datetime import datetime
from flask import Blueprint, jsonify
from flask.ext.login import current_user
from app.api import auto
from app.api.constants import BAD_REQUEST, OK
from app.api.helpers import response_builder
from app.api.sets.model import Set, UserSet
from app.api.users.constants import FOREVER, MONTH


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
    information = set_response_builder(set)
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
        information = set_response_builder(set)
        sets.append(information)
    ids = []
    sets_ids = Set.query.all()
    for set_id in sets_ids:
        ids.append(set_id.id)
    return jsonify({'error_code': OK, 'result': sets, 'ids': ids}), 200


def set_response_builder(set, excluded=[]):
    information = response_builder(set, Set, excluded)
    if not current_user.is_authenticated():
        information['is_open'] = False
    else:
        user_set = UserSet.query.filter_by(set_id=set.id, user_id=current_user.id).first()
        if user_set:
            if user_set.open_type == FOREVER:
                information['is_open'] = True
            if user_set.open_type == MONTH:
                if (datetime.utcnow() - user_set.open_date).days <= 30:
                    information['is_open'] = True
                else:
                    information['is_open'] = False
        else:
            information['is_open'] = False
    return information