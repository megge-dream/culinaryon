from flask import request, jsonify, g, url_for, Blueprint
from flask.ext.login import login_required
from sqlalchemy import distinct

from app.api import db, auto
from app.api.categories.model import Category
from app.api.constants import OK, BAD_REQUEST
from app.api.cuisine_types.model import CuisineType
from app.api.helpers import *
from app.api.ingredients.model import Ingredient
from app.api.likes.model import Like
from app.api.photos.model import RecipePhoto
from app.api.recipes.model import Recipe, InstructionItem
from app.api.sets.model import Set, UserSet
from app.api.tools.model import Tool
from app.api.users.constants import FOREVER, MONTH
from app.api.wines.model import Wine
from app.decorators import admin_required


mod = Blueprint('recipes_v2', __name__, url_prefix='/api_v2/recipes')

@auto.doc()
@mod.route('/<int:id>', methods=['GET'])
def get_recipe(id):
    """
    Get information about recipe.
    :param id: recipe id
    :return: json with parameters:
            error_code - server response_code
            result - information about recipe
    """
    recipe = Recipe.query.get(id)
    if not recipe:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # recipe with `id` isn't exist
    information = recipe_response_builder(recipe)
    information['ingredients'] = get_ingredients_by_divisions(id)
    hash_of_information = make_hash(information)
    information['hash'] = hash_of_information
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/', methods=['GET'])
def get_all_recipes():
    """
    Get information about all exist recipes.
    :param offset (GET param) : starts from which recipe
    :param limit (GET param) : how many recipes you want to get
    :return: json with parameters:
            error_code - server response_code
            result - information about recipes
            entities_count - numbers of all recipes
    """
    recipes = []
    offset = request.args.get('offset', default=0, type=int)
    limit = request.args.get('limit', type=int)
    count = Recipe.query.count()
    if limit is not None and offset is not None:
        # for faster loading
        limit = 5
        recipes_band = Recipe.query.slice(start=offset, stop=limit+offset).all()
    else:
        recipes_band = Recipe.query.all()
    for recipe in recipes_band:
        # information = response_builder(recipe, Recipe, excluded=['description', 'spicy', 'complexity', 'time',
        #                                                          'amount_of_persons', 'chef_id', 'video'])
        # categories = []
        # for category in Recipe.query.filter_by(id=recipe.id).first().categories:
        #     categories.append(category.id)
        # information['categories'] = []
        # if categories is not None:
        #     for category_id in categories:
        #         category = Category.query.get(category_id)
        #         category_information = response_builder(category, Category)
        #         information["categories"].append(category_information)
        # information['photos'] = []
        # for photo in RecipePhoto.query.filter_by(item_id=recipe.id):
        #     photo_information = response_builder(photo, RecipePhoto)
        #     information['photos'].append(photo_information)
        information = recipe_response_builder(recipe)
        information['ingredients'] = get_ingredients_by_divisions(recipe.id)
        hash_of_information = make_hash(information)
        information['hash'] = hash_of_information
        recipes.append(information)
    ids = []
    recipes_ids = Recipe.query.all()
    for recipe_id in recipes_ids:
        ids.append(recipe_id.id)
    return jsonify({'error_code': OK, 'result': recipes, 'entities_count': count, 'ids': ids}), 200


@auto.doc()
@mod.route('/chef/id=<int:id>', methods=['GET'])
def get_chef_recipes(id):
    """
    Get information about all recipes for chef with special id.
    :param id: chef id
    :param offset (GET param) : starts from which recipes
    :param limit (GET param) : how many recipes you want to get
    :return: json with parameters:
            error_code - server response_code
            result - information about recipes
            entities_count - numbers of all chefs recipes
    """
    recipes = []
    offset = request.args.get('offset', default=0, type=int)
    limit = request.args.get('limit', type=int)
    count = Recipe.query.filter_by(chef_id=id).count()
    if limit is not None and offset is not None:
        recipes_band = Recipe.query.filter_by(chef_id=id).slice(start=offset, stop=limit+offset).all()
    else:
        recipes_band = Recipe.query.filter_by(chef_id=id)
    for recipe in recipes_band:
        information = recipe_response_builder(recipe)
        information['ingredients'] = get_ingredients_by_divisions(recipe.id)
        hash_of_information = make_hash(information)
        information['hash'] = hash_of_information
        recipes.append(information)
    return jsonify({'error_code': OK, 'result': recipes, 'entities_count': count}), 200


@auto.doc()
@mod.route('/category/id=<int:id>', methods=['GET'])
def get_category_recipes(id):
    """
    Get information about all recipes in category with special id.
    :param id: category id
    :param offset (GET param) : starts from which recipes
    :param limit (GET param) : how many recipes you want to get
    :return: json with parameters:
            error_code - server response_code
            result - information about recipes
            entities_count - numbers of all chefs recipes
    """
    recipes = []
    offset = request.args.get('offset', default=0, type=int)
    limit = request.args.get('limit', type=int)
    count = Recipe.query.join(Category.recipes).filter(Category.id == id).count()
    if limit is not None and offset is not None:
        recipes_band = Recipe.query.join(Category.recipes).filter(Category.id == id).slice(start=offset, stop=limit+offset).all()
    else:
        recipes_band = Recipe.query.join(Category.recipes).filter(Category.id == id).all()
    for recipe in recipes_band:
        information = recipe_response_builder(recipe)
        information['ingredients'] = get_ingredients_by_divisions(recipe.id)
        hash_of_information = make_hash(information)
        information['hash'] = hash_of_information
        recipes.append(information)
    return jsonify({'error_code': OK, 'result': recipes, 'entities_count': count}), 200


@auto.doc()
@mod.route('/set/id=<int:id>', methods=['GET'])
def get_set_recipes(id):
    """
    Get information about all recipes in set with special id.
    :param id: set id
    :param offset (GET param) : starts from which recipes
    :param limit (GET param) : how many recipes you want to get
    :return: json with parameters:
            error_code - server response_code
            result - information about recipes
            entities_count - numbers of all chefs recipes
    """
    recipes = []
    offset = request.args.get('offset', default=0, type=int)
    limit = request.args.get('limit', type=int)
    count = Recipe.query.join(Set.recipes).filter(Set.id == id).count()
    if limit is not None and offset is not None:
        recipes_band = Recipe.query.join(Set.recipes).filter(Set.id == id).slice(start=offset, stop=limit+offset).all()
    else:
        recipes_band = Recipe.query.join(Set.recipes).filter(Set.id == id).all()
    for recipe in recipes_band:
        information = recipe_response_builder(recipe)
        information['ingredients'] = get_ingredients_by_divisions(recipe.id)
        hash_of_information = make_hash(information)
        information['hash'] = hash_of_information
        recipes.append(information)
    return jsonify({'error_code': OK, 'result': recipes, 'entities_count': count}), 200


def recipe_response_builder(recipe, excluded=[]):
    categories = []
    for category in Recipe.query.filter_by(id=recipe.id).first().categories:
        categories.append(category.id)
    cuisine_types = []
    for cuisine_type in Recipe.query.filter_by(id=recipe.id).first().cuisine_types:
        cuisine_types.append(cuisine_type.id)
    tools = []
    for tool in Recipe.query.filter_by(id=recipe.id).first().tools:
        tools.append(tool.id)
    wines = []
    for wine in Recipe.query.filter_by(id=recipe.id).first().wines:
        wines.append(wine.id)
    information = response_builder(recipe, Recipe, excluded)
    information['categories'] = []
    if categories is not None:
        for category_id in categories:
            category = Category.query.get(category_id)
            category_information = response_builder(category, Category)
            information["categories"].append(category_information)
    information['cuisine_types'] = []
    if cuisine_types is not None:
        for cuisine_type_id in cuisine_types:
            cuisine_type = CuisineType.query.get(cuisine_type_id)
            cuisine_type_information = response_builder(cuisine_type, CuisineType)
            information["cuisine_types"].append(cuisine_type_information)
    information['tools'] = []
    if tools is not None:
        for tool_id in tools:
            tool = Tool.query.get(tool_id)
            tool_information = response_builder(tool, Tool)
            information["tools"].append(tool_information)
    information['wines'] = []
    if wines is not None:
        for wine_id in wines:
            wine = Wine.query.get(wine_id)
            wine_information = response_builder(wine, Wine)
            information["wines"].append(wine_information)
    information['photos'] = []
    for photo in RecipePhoto.query.filter_by(item_id=recipe.id):
        photo_information = response_builder(photo, RecipePhoto)
        information['photos'].append(photo_information)
    information['ingredients'] = []
    for ingredient in Ingredient.query.filter_by(recipe_id=recipe.id):
        ingredient_information = response_builder(ingredient, Ingredient, excluded=["recipe_id"])
        information['ingredients'].append(ingredient_information)
    information['instructions'] = []
    for instruction in InstructionItem.query.filter_by(recipe_id=recipe.id):
        instruction_information = response_builder(instruction, InstructionItem, excluded=["recipe_id"])
        information['instructions'].append(instruction_information)
    information['likes'] = Like.query.filter_by(recipe_id=recipe.id).count()
    if not recipe.set_id:
        information['is_open'] = True
    elif UserSet.query.filter_by(set_id=recipe.set_id, user_id=current_user.id).first():
        user_set = UserSet.query.filter_by(set_id=recipe.set_id, user_id=current_user.id).first()
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