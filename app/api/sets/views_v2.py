# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request
from flask.ext.login import login_required, current_user
from app.api import auto, db
from app.api.constants import BAD_REQUEST, OK
from app.api.recipes.views_v2 import recipe_response_builder, set_response_builder
from app.api.sets.model import Set, UserSet
from app.api.users.constants import FOREVER


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
    lang = request.args.get('lang', type=unicode, default=u'en')
    set = Set.query.get(id)
    if not set:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # set with `id` isn't exist
    information = set_response_builder(set, lang)
    information['recipes'] = []
    for recipe in set.recipes:
        information['recipes'].append(recipe_response_builder(recipe, lang))
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/', methods=['GET'])
def get_all_sets():
    """
    Get information about all exist sets.
    :param offset (GET param) : starts from which set
    :param limit (GET param) : how many sets you want to get
    :return: json with parameters:
            error_code - server response_code
            result - information about sets
            entities_count - number of sets
            ids - ids of all sets
    """
    lang = request.args.get('lang', type=unicode, default=u'en')
    sets = []
    offset = request.args.get('offset', default=0, type=int)
    limit = request.args.get('limit', type=int)
    count = Set.query.count()
    # if limit is not None and offset is not None:
    #     sets_band = Set.query.slice(start=offset, stop=limit+offset).all()
    # else:
    #     sets_band = Set.query.all()
    sets_band = Set.query.all()
    for set in sets_band:
        information = set_response_builder(set, lang)
        sets.append(information)
    sets = sorted(sets, key=lambda k: k['is_open'], reverse=True)
    if limit is not None and offset is not None:
        sets = sets[offset:limit+offset]
    ids = []
    sets_ids = Set.query.all()
    for set_id in sets_ids:
        ids.append(set_id.id)
    return jsonify({'error_code': OK, 'result': sets, 'ids': ids, 'entities_count': count}), 200


@auto.doc()
@mod.route('/buy_set', methods=['POST'])
@login_required
def buy_set():
    """
    Buy set with store id in json. List of parameters in json request (one of them is required):
            store_id
    Example of request:
            {"store_id": "1"}
    :return: json with parameters:
            error_code - server response_code
            result - information about set
    """
    lang = request.args.get('lang', type=unicode, default=u'en')
    store_id = request.json.get('store_id')
    if store_id is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'missing arguments'}), 200  # missing arguments
    set = Set.query.filter_by(store_id=store_id).first()
    if not set:
        set = Set.query.filter_by(sale_store_id=store_id).first()
    if not set:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'set not exist'}), 200
    user_set = UserSet(user_id=current_user.id, set_id=set.id, open_type=FOREVER)
    db.session.add(user_set)
    db.session.commit()
    information = set_response_builder(set, lang)
    information['recipes'] = []
    for recipe in set.recipes:
        information['recipes'].append(recipe_response_builder(recipe, lang))
    return jsonify({'error_code': OK, 'result': information}), 200
