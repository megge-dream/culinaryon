from flask import Blueprint, jsonify, request
from flask.ext.login import login_required, current_user

from app.api import db, auto
from app.api.constants import BAD_REQUEST, OK
from app.api.helpers import response_builder
from app.api.likes.model import Like
from app.api.users.model import User


mod = Blueprint('likes', __name__, url_prefix='/api/likes')


@auto.doc()
@mod.route('/', methods=['POST'])
@login_required
def new_like():
    """
    Add new like. List of parameters in json request:
            user_id (required)
            recipe_id (required)
    Example of request:
            {"user_id":3, "recipe_id":2}
    :return: json with parameters:
            error_code - server response_code
            amount - new amount of likes for recipes with recipe_id
            result - information about created like
    """
    user_id = request.json.get('user_id')
    recipe_id = request.json.get('recipe_id')
    if user_id is None or recipe_id is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # missing arguments
    if current_user.id == user_id:
        like = Like.query.filter_by(recipe_id=recipe_id, user_id=user_id).first()
        if like:
            db.session.delete(like)
        else:
            like = Like(user_id=user_id, recipe_id=recipe_id)
            db.session.add(like)
        db.session.commit()
        amount = Like.query.filter_by(recipe_id=recipe_id).count()
        return jsonify({'error_code': OK, 'amount': amount}), 200
    else:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['GET'])
def get_likes(id):
    """
    Get likes for recipe.
    :param id: recipe id
    :return: json with parameters:
            error_code - server response_code
            amount - amount of likes
            users - information about users who likes this recipe
    """
    liked_users = []
    amount = Like.query.filter_by(recipe_id=id).count()
    for like in Like.query.filter_by(recipe_id=id):
        information = response_builder(User.query.get(like.user_id), User, excluded=['password'])
        liked_users.append(information)
    return jsonify({'error_code': OK, 'amount': amount, 'users': liked_users}), 200


@auto.doc()
@mod.route('/<int:recipe_id>', methods=['DELETE'])
@login_required
def delete_like(recipe_id):
    """
    Delete like for recipe from current user.
    :param recipe_id: recipe id
    :return: json with parameters:
            error_code - server response_code
    """
    like = Like.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first()
    if not like:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # like with `id` isn't exist
    db.session.delete(like)
    db.session.commit()
    return jsonify({'error_code': OK}), 200
