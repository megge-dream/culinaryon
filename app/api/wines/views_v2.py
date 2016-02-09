import datetime
from flask import request, jsonify, g, url_for, Blueprint
from flask.ext.login import login_required

from app.api import db, auto
from app.api.constants import BAD_REQUEST, OK
from app.api.helpers import *
from app.api.likes.model import LikeWine, Like
from app.api.sets.model import UserSet, VendorSet
from app.api.cuisine_types.model import CuisineType
from app.api.users.constants import FOREVER, MONTH
from app.api.wines.model import Wine
from app.decorators import admin_required


mod = Blueprint('wines_v2', __name__, url_prefix='/api_v2/wines')


@auto.doc()
@mod.route('/', methods=['POST'])
@login_required
@admin_required
def new_wine():
    """
    Add new wine. List of parameters in json request:
            title (required)
    Example of request:
            {"title":"good"}
    :return: json with parameters:
            error_code - server response_code
            result - information about created wine
    """
    title = request.json.get('title')
    if title is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # missing arguments
    wine = Wine(title=title)
    db.session.add(wine)
    db.session.commit()
    information = response_builder(wine, Wine)
    return jsonify({'error_code': OK, 'result': information}), 201


@auto.doc()
@mod.route('/<int:id>', methods=['PUT'])
@login_required
@admin_required
def update_wine(id):
    """
    Update exists wine. List of parameters in json request:
            title (optional)
    Example of request:
            {"title":"good"}
    :param id: wine id
    :return: json with parameters:
            error_code - server response_code
            result - information about updated wine
    """
    wine = Wine.query.get(id)
    if not wine:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200
    if request.json.get('title'):
        wine.title = request.json.get('title')
    db.session.commit()
    wine = Wine.query.get(id)
    information = response_builder(wine, Wine)
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['GET'])
def get_wine(id):
    """
    Get information about wine.
    :param id: wine id
    :return: json with parameters:
            error_code - server response_code
            result - information about wine
    """
    lang = request.args.get('lang', type=unicode, default=u'en')
    vendor_id = request.args.get('vendor_id', type=unicode, default=u'')
    wine = Wine.query.get(id)
    if not wine:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # wine with `id` isn't exist
    information = wine_response_builder(wine, lang, vendor_id)
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/', methods=['GET'])
def get_all_wines():
    """
    Get information about all exist wines.
    :return: json with parameters:
            error_code - server response_code
            result - information about wines
    """
    lang = request.args.get('lang', type=unicode, default=u'en')
    vendor_id = request.args.get('vendor_id', type=unicode, default=u'')
    wines = []
    for wine in Wine.query.all():
        information = wine_response_builder(wine, lang, vendor_id)
        wines.append(information)
    return jsonify({'error_code': OK, 'result': wines}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_wine(id):
    """
    Delete wine.
    :param id: wine id
    :return: json with parameters:
            error_code - server response_code
    """
    wine = Wine.query.get(id)
    if not wine:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # wine with `id` isn't exist
    db.session.delete(wine)
    db.session.commit()
    return jsonify({'error_code': OK}), 200


def wine_response_builder(wine, lang=u'en', vendor_id=u'', excluded=[]):
    information = response_builder(wine, Wine, lang, excluded=excluded)
    information['likes'] = LikeWine.query.filter_by(wine_id=wine.id).count()
    information['recipes'] = []
    if 'recipes' in excluded:
        for recipe in wine.recipes:
            information['recipes'].append(recipe_without_wines_response_builder(recipe, lang, vendor_id, excluded=excluded))
    return information


def recipe_without_wines_response_builder(recipe, lang=u'en', vendor_id=u'', excluded=[]):
    categories = []
    recipe_query = Recipe.query
    # if current_user.is_authenticated() and current_user.role_code == 0:
    #     recipe_query = Recipe.query
    # else:
    #     recipe_query = Recipe.query.filter_by(type=PUBLISHED)
    for category in recipe_query.filter_by(id=recipe.id).first().categories:
        categories.append(category.id)
    cuisine_types = []
    for cuisine_type in recipe_query.filter_by(id=recipe.id).first().cuisine_types:
        cuisine_types.append(cuisine_type.id)
    tools = []
    for tool in recipe_query.filter_by(id=recipe.id).first().tools:
        tools.append(tool.id)
    information = response_builder(recipe, Recipe, lang, excluded=excluded)
    information['categories'] = []
    if categories is not None:
        for category_id in categories:
            category = Category.query.get(category_id)
            category_information = response_builder(category, Category, lang)
            information["categories"].append(category_information)
    information['cuisine_types'] = []
    if cuisine_types is not None:
        for cuisine_type_id in cuisine_types:
            cuisine_type = CuisineType.query.get(cuisine_type_id)
            cuisine_type_information = response_builder(cuisine_type, CuisineType, lang)
            information["cuisine_types"].append(cuisine_type_information)
    information['tools'] = []
    if tools is not None:
        for tool_id in tools:
            tool = Tool.query.get(tool_id)
            tool_information = response_builder(tool, Tool, lang)
            information["tools"].append(tool_information)
    information['photos'] = []
    for photo in RecipePhoto.query.filter_by(item_id=recipe.id):
        photo_information = response_builder(photo, RecipePhoto, lang)
        information['photos'].append(photo_information)
    information['ingredients'] = []
    for ingredient in Ingredient.query.filter_by(recipe_id=recipe.id):
        ingredient_information = response_builder(ingredient, Ingredient, lang, excluded=["recipe_id"])
        information['ingredients'].append(ingredient_information)
    information['instructions'] = []
    for instruction in InstructionItem.query.filter_by(recipe_id=recipe.id):
        instruction_information = response_builder(instruction, InstructionItem, lang, excluded=["recipe_id"])
        information['instructions'].append(instruction_information)
    information['likes'] = Like.query.filter_by(recipe_id=recipe.id).count()
    if not recipe.set_id:
        information['is_open'] = True
    elif Set.query.get(recipe.set_id).is_free:
        information['is_open'] = True
    elif not current_user.is_authenticated():
        information['is_open'] = False
    # elif UserSet.query.filter_by(set_id=recipe.set_id, user_id=current_user.id).first():
        # user_set = UserSet.query.filter_by(set_id=recipe.set_id, user_id=current_user.id).first()
    elif VendorSet.query.filter_by(set_id=recipe.set_id, vendor_id=vendor_id).first():
        information['is_open'] = True
    else:
        information['is_open'] = False
    return information