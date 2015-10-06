# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request
from flask.ext.login import login_required
from app.api import auto
from app.api.constants import BAD_REQUEST, OK
from app.api.promo_codes.model import PromoCode
from app.decorators import admin_required


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
    promo_code = promo_code.split('-')
    promo_code_entity = PromoCode.query.filter(PromoCode.code.ilike(promo_code[2]),
                                               PromoCode.id == promo_code[0].split('0')[-1],
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
    return jsonify({'error_code': OK, 'result': result}), 201