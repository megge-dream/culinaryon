from flask import Blueprint, jsonify, request, g
from flask.ext.login import current_user, login_required

from app.api import db, auto
from app.api.basket.model import Basket
from app.api.constants import BAD_REQUEST, OK
from app.api.helpers import response_builder
from app.api.ingredients.model import Ingredient
from app.decorators import admin_required

mod = Blueprint('basket', __name__, url_prefix='/api/baskets')


@auto.doc()
@mod.route('/', methods=['POST'])
@login_required
def new_basket():
    """
    Add new basket. List of parameters in json request:
            user_id (required)
            ingredient_id (required)
            amount (required)
            is_to_buy (optional)
            is_in_stock (optional)
    Example of request:
            {"user_id":1, "ingredient_id":1, "amount":1}
    :return: json with parameters:
            error_code - server response_code
            result - information about created basket
    """
    user_id = request.json.get('user_id')
    if current_user.id == user_id:
        ingredient_id = request.json.get('ingredient_id')
        amount = request.json.get('amount')
        is_to_buy = request.json.get('is_to_buy')
        is_in_stock = request.json.get('is_in_stock')
        if user_id is None or ingredient_id is None or amount is None:
            return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # missing arguments
        basket = Basket(user_id=user_id, ingredient_id=ingredient_id, amount=amount, is_in_stock=is_in_stock,
                        is_to_buy=is_to_buy)
        db.session.add(basket)
        db.session.commit()
        information = response_builder(basket, Basket)
        return jsonify({'error_code': OK, 'result': information}), 201
    else:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['GET'])
@login_required
def get_baskets(id):
    """
    Get baskets for user by his id.
    :param id: user id
    :return: json with parameters:
            error_code - server response_code
            baskets - information about baskets
    """
    baskets = Basket.query.filter_by(user_id=id)
    baskets_info = []
    for basket in baskets:
        information = response_builder(basket, Basket, excluded=['user_id', 'ingredient_id'])
        ingredient = Ingredient.query.get(basket.ingredient_id)
        information['ingredient'] = response_builder(ingredient, Ingredient, excluded=['recipe_id', 'creation_date'])
        baskets_info.append(information)
    return jsonify({'error_code': OK, 'baskets': baskets_info}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_basket(id):
    """
    Delete basket.
    :param id: basket id
    :return: json with parameters:
            error_code - server response_code
    """
    basket = Basket.query.get(id)
    if not basket:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # favorite with `id` isn't exist
    if current_user.id == basket.user_id:
        db.session.delete(basket)
        db.session.commit()
        return jsonify({'error_code': OK}), 200
    else:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200