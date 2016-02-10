# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request
from flask.ext.login import login_required
from app.api import auto, db
from app.api.constants import BAD_REQUEST, OK
from app.api.promo_codes.model import PromoCode
from app.api.recipes.views_v2 import set_response_builder, recipe_response_builder
from app.api.sets.model import VendorSet, Set
from app.decorators import admin_required
import re


mod = Blueprint('promo_codes', __name__, url_prefix='/api_v2/promo_codes')


@auto.doc()
@mod.route('/', methods=['POST'])
def get_promo_code_info():
    """
    Get information about promo code. List of parameters in json request:
            promo_code (required)
    Example of request:
            {"promo_code":"0000-1111-OHYH"}
    :return: json with parameters:
            error_code - server response_code
            result - is promo code correct
    """
    promo_code = request.json.get('promo_code')
    if promo_code is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # missing arguments
    pattern = re.compile("^[0-9]{4}-[0-9]{4}-[A-Z]{4}$")
    if not pattern.match(promo_code):
        return jsonify({'error_code': BAD_REQUEST, 'result': 'wrong format'}), 200  # missing arguments
    promo_code = promo_code.split('-')
    promo_code_entity = PromoCode.query.filter(PromoCode.code.ilike(promo_code[2]),
                                               PromoCode.id == int(promo_code[0]),
                                               PromoCode.value == promo_code[1]).first()
    if promo_code_entity:
        is_correct = True
    else:
        is_correct = False
    return jsonify({'error_code': OK, 'result': is_correct}), 200


@auto.doc()
@mod.route('/', methods=['GET'])
@login_required
@admin_required
def get_all_promo_codes():
    """
    Get all promo codes.
    :return: json with parameters:
            error_code - server response_code
            result - all promo codes
    """
    result = []
    promo_codes = list(PromoCode.query.all())
    for promo_code in promo_codes:
        result.append(unicode(promo_code))
    return jsonify({'error_code': OK, 'result': result}), 200


@auto.doc()
@mod.route('/open', methods=['POST'])
def open_with_promo():
    """
    Open set by promo code. List of parameters in json request:
            promo_code (required)
            set_id (required)
    Example of request:
            {"promo_code":"0000-1111-OHYH", "set_id": 1}
    :return: json with parameters:
            error_code - server response_code
            result - info about opened set
    """
    promo_code = request.json.get('promo_code')
    set_id = request.json.get('set_id')
    lang = request.args.get('lang', type=unicode, default=u'en')
    vendor_id = request.args.get('vendor_id', type=unicode, default=u'')
    if promo_code is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # missing arguments
    pattern = re.compile("^[0-9]{4}-[0-9]{4}-[A-Z]{4}$")
    if not pattern.match(promo_code):
        return jsonify({'error_code': BAD_REQUEST, 'result': 'wrong format'}), 200  # missing arguments
    promo_code = promo_code.split('-')
    promo_code_entity = PromoCode.query.filter(PromoCode.code.ilike(promo_code[2]),
                                               PromoCode.id == int(promo_code[0]),
                                               PromoCode.value == promo_code[1]).first()
    if not promo_code_entity:
        return jsonify({'error_code': OK, 'result': 'promo is incorrect'}), 200
    vendor_set = VendorSet(vendor_id=vendor_id, set_id=set_id)
    db.session.add(vendor_set)
    db.session.commit()
    set = Set.query.filter_by(id=set_id).first()
    information = set_response_builder(set, lang, vendor_id)
    information['recipes'] = []
    for recipe in set.recipes:
        information['recipes'].append(recipe_response_builder(recipe, lang, vendor_id))
    return jsonify({'error_code': OK, 'result': information}), 200
