from flask import Blueprint, jsonify, request, g
from flask.ext.login import login_required, current_user

from app.api import db, auto
from app.api.categories.model import Category
from app.api.constants import OK, BAD_REQUEST
from app.api.helpers import response_builder
from app.api.favorites.model import Favorite
from app.api.photos.model import RecipePhoto
from app.api.recipes.model import Recipe
from app.api.recipes.views import recipe_response_builder

mod = Blueprint('favorites', __name__, url_prefix='/api/favorites')


@auto.doc()
@mod.route('/', methods=['POST'])
@login_required
def new_favorite():
    """
    Add new favorite. List of parameters in json request:
            user_id (required)
            recipe_id (required)
    Example of request:
            {"user_id":3, "recipe_id":2}
    :return: json with parameters:
            error_code - server response_code
            result - information about created favorite
    """
    user_id = request.json.get('user_id')
    recipe_id = request.json.get('recipe_id')
    if user_id is None or recipe_id is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # missing arguments
    if current_user.id == user_id:
    # if True:
        favorite = Favorite.query.filter_by(recipe_id=recipe_id, user_id=user_id).first()
        if not favorite:
            favorite = Favorite(user_id=user_id, recipe_id=recipe_id)
            db.session.add(favorite)
        db.session.commit()
        information = response_builder(favorite, Favorite)
        return jsonify({'error_code': OK, 'result': information}), 201
    else:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200


@auto.doc()
@mod.route('/', methods=['GET'])
@login_required
def get_favorite():
    """
    Get favorites for current user.
    :return: json with parameters:
            error_code - server response_code
            recipes - information about favorites recipes
    """
    user_id = current_user.id
    favorites = Favorite.query.filter_by(user_id=user_id)
    recipes = []
    for favorite in favorites:
        recipe = Recipe.query.get(favorite.recipe_id)
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
        recipes.append(information)
    return jsonify({'error_code': OK, 'recipes': recipes}), 200


@auto.doc()
@mod.route('/<int:recipe_id>', methods=['DELETE'])
@login_required
def delete_favorite(recipe_id):
    """
    Delete recipe from current user favorites.
    :param recipe_id: recipe id
    :return: json with parameters:
            error_code - server response_code
    """
    favorite = Favorite.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first()
    if not favorite:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # favorite isn't exist
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({'error_code': OK}), 200
