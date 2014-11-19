from flask import request, jsonify, g, url_for, Blueprint

from app.api import db
from app.api.helpers import *
from app.api.ingredients.model import Ingredient


mod = Blueprint('ingredients', __name__, url_prefix='/api/ingredients')


# {"title":"good", "amount":2, "unit":"spoon", "recipe_id":1}
@mod.route('/', methods=['POST'])
def new_ingredient():
    title = request.json.get('title')
    amount = request.json.get('amount')
    unit = request.json.get('unit')
    recipe_id = request.json.get('recipe_id')
    if title is None:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # missing arguments
    ingredient = Ingredient(title=title, unit=unit, amount=amount, recipe_id=recipe_id)
    db.session.add(ingredient)
    db.session.commit()
    information = response_builder(ingredient, Ingredient)
    return jsonify({'error_code': 201, 'result': information}), 201


@mod.route('/<int:id>', methods=['PUT'])
def update_ingredient(id):
    ingredient = Ingredient.query.get(id)
    if not ingredient:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200
    if request.json.get('title'):
        ingredient.title = request.json.get('title')
    if request.json.get('amount'):
        ingredient.amount = request.json.get('amount')
    if request.json.get('unit'):
        ingredient.unit = request.json.get('unit')
    if request.json.get('recipe_id'):
        ingredient.recipe_id = request.json.get('recipe_id')
    db.session.commit()
    ingredient = Ingredient.query.get(id)
    information = response_builder(ingredient, Ingredient)
    return jsonify({'error_code': 200, 'result': information}), 200


@mod.route('/<int:id>', methods=['GET'])
def get_ingredient(id):
    ingredient = Ingredient.query.get(id)
    if not ingredient:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # ingredient with `id` isn't exist
    information = response_builder(ingredient, Ingredient)
    return jsonify({'error_code': 200, 'result': information}), 200


@mod.route('/', methods=['GET'])
def get_all_ingredients():
    ingredients = []
    for ingredient in Ingredient.query.all():
        information = response_builder(ingredient, Ingredient)
        ingredients.append(information)
    return jsonify({'error_code': 200, 'result': ingredients}), 200


@mod.route('/<int:id>', methods=['DELETE'])
def delete_ingredient(id):
    ingredient = Ingredient.query.get(id)
    if not ingredient:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # ingredient with `id` isn't exist
    db.session.delete(ingredient)
    db.session.commit()
    return jsonify({'error_code': 200}), 200


@mod.route('/recipes/<int:id>', methods=['GET'])
def get_recipe_ingredients(id):
    ingredients = []
    for ingredient in Ingredient.query.filter_by(recipe_id=id):
        information = response_builder(ingredient, Ingredient, excluded=["recipe_id"])
        ingredients.append(information)
    return jsonify({'error_code': 200, 'result': ingredients}), 200
