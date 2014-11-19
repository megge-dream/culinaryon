from flask import Blueprint, jsonify, request, g

from app.api import db
from app.api.basket.model import Basket
from app.api.helpers import response_builder
from app.api.ingredients.model import Ingredient

mod = Blueprint('basket', __name__, url_prefix='/api/baskets')


# {"user_id":1, "ingredient_id":1, "amount":1}
@mod.route('/', methods=['POST'])
def new_basket():
    user_id = request.json.get('user_id')
    ingredient_id = request.json.get('ingredient_id')
    amount = request.json.get('amount')
    is_to_buy = request.json.get('is_to_buy')
    is_in_stock = request.json.get('is_in_stock')
    if user_id is None or ingredient_id is None or amount is None:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # missing arguments
    basket = Basket(user_id=user_id, ingredient_id=ingredient_id, amount=amount, is_in_stock=is_in_stock,
                    is_to_buy=is_to_buy)
    db.session.add(basket)
    db.session.commit()
    information = response_builder(basket, Basket)
    return jsonify({'error_code': 201, 'result': information}), 201


@mod.route('/<int:id>', methods=['GET'])
def get_basket(id):
    baskets = Basket.query.filter_by(user_id=id)
    baskets_info = []
    for basket in baskets:
        information = response_builder(basket, Basket, excluded=['user_id', 'ingredient_id'])
        ingredient = Ingredient.query.get(basket.ingredient_id)
        information['ingredient'] = response_builder(ingredient, Ingredient, excluded=['recipe_id', 'creation_date'])
        baskets_info.append(information)
    return jsonify({'error_code': 200, 'baskets': baskets_info}), 200


@mod.route('/<int:id>', methods=['DELETE'])
def delete_basket(id):
    basket = Basket.query.get(id)
    if not basket:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # favorite with `id` isn't exist
    db.session.delete(basket)
    db.session.commit()
    return jsonify({'error_code': 200}), 200