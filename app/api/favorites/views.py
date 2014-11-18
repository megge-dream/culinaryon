from flask import Blueprint, jsonify, request, g

from app.api import db
from app.api.helpers import response_builder
from app.api.favorites.model import Favorite
from app.api.recipes.model import Recipe

mod = Blueprint('favorites', __name__, url_prefix='/api/favorites')


# {"user_id":3, "recipe_id":2}
@mod.route('/', methods=['POST'])
def new_favorite():
    user_id = request.json.get('user_id')
    recipe_id = request.json.get('recipe_id')
    if user_id is None or recipe_id is None:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # missing arguments
    favorite = Favorite(user_id=user_id, recipe_id=recipe_id)
    db.session.add(favorite)
    db.session.commit()
    information = response_builder(favorite, Favorite)
    return jsonify({'error_code': 201, 'result': information}), 201


@mod.route('/', methods=['GET'])
def get_favorite():
    # user_id = g.user.id
    # for test
    user_id = 1
    favorites = Favorite.query.filter_by(user_id=user_id)
    recipes = []
    for favorite in favorites:
        information = response_builder(Recipe.query.get(favorite.recipe_id), Recipe)
        recipes.append(information)
    return jsonify({'error_code': 200, 'recipes': recipes}), 200


@mod.route('/<int:id>', methods=['DELETE'])
def delete_favorite(id):
    favorite = Favorite.query.get(id)
    if not favorite:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # favorite with `id` isn't exist
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({'error_code': 200}), 200