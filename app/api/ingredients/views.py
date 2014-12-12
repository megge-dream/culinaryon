from flask import request, jsonify, g, url_for, Blueprint
from flask.ext.login import login_required

from app.api import db, auto
from app.api.constants import BAD_REQUEST, OK
from app.api.helpers import *
from app.api.ingredients.model import Ingredient
from app.decorators import admin_required


mod = Blueprint('ingredients', __name__, url_prefix='/api/ingredients')


@auto.doc()
@mod.route('/', methods=['POST'])
@login_required
@admin_required
def new_ingredient():
    """
    Add new ingredient. List of parameters in json request:
            title (required)
            amount (optional)
            unit (optional)
            recipe_id (optional)
    Example of request:
            {"title":"good", "amount":2, "unit":"spoon", "recipe_id":1}
    :return: json with parameters:
            error_code - server response_code
            result - information about created ingredient
    """
    title = request.json.get('title')
    amount = request.json.get('amount')
    unit = request.json.get('unit')
    recipe_id = request.json.get('recipe_id')
    if title is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # missing arguments
    ingredient = Ingredient(title=title, unit=unit, amount=amount, recipe_id=recipe_id)
    db.session.add(ingredient)
    db.session.commit()
    information = response_builder(ingredient, Ingredient)
    return jsonify({'error_code': OK, 'result': information}), 201


@auto.doc()
@mod.route('/<int:id>', methods=['PUT'])
@login_required
@admin_required
def update_ingredient(id):
    """
    Update exists ingredient. List of parameters in json request:
            title (optional)
            amount (optional)
            unit (optional)
            recipe_id (optional)
    Example of request:
            {"title":"good", "amount":6, "unit":"spoon"}
    :param id: ingredient id
    :return: json with parameters:
            error_code - server response_code
            result - information about updated ingredient
    """
    ingredient = Ingredient.query.get(id)
    if not ingredient:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200
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
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['GET'])
@login_required
def get_ingredient(id):
    """
    Get information about ingredient.
    :param id: ingredient id
    :return: json with parameters:
            error_code - server response_code
            result - information about ingredient
    """
    ingredient = Ingredient.query.get(id)
    if not ingredient:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # ingredient with `id` isn't exist
    information = response_builder(ingredient, Ingredient)
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/', methods=['GET'])
@login_required
def get_all_ingredients():
    """
    Get information about all exist ingredients.
    :return: json with parameters:
            error_code - server response_code
            result - information about ingredients
    """
    ingredients = []
    for ingredient in Ingredient.query.all():
        information = response_builder(ingredient, Ingredient)
        ingredients.append(information)
    return jsonify({'error_code': OK, 'result': ingredients}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_ingredient(id):
    """
    Delete ingredient.
    :param id: ingredient id
    :return: json with parameters:
            error_code - server response_code
    """
    ingredient = Ingredient.query.get(id)
    if not ingredient:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # ingredient with `id` isn't exist
    db.session.delete(ingredient)
    db.session.commit()
    return jsonify({'error_code': OK}), 200


@auto.doc()
@mod.route('/recipes/<int:id>', methods=['GET'])
@login_required
def get_recipe_ingredients(id):
    """
    Get information about all ingredients for recipe with special id.
    :param id: recipe id
    :return: json with parameters:
            error_code - server response_code
            result - information about ingredients
    """
    ingredients = []
    for ingredient in Ingredient.query.filter_by(recipe_id=id):
        information = response_builder(ingredient, Ingredient, excluded=["recipe_id"])
        ingredients.append(information)
    return jsonify({'error_code': OK, 'result': ingredients}), 200
