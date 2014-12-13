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
            result - information about created like
    """
    user_id = request.json.get('user_id')
    if current_user.id == user_id:
        recipe_id = request.json.get('recipe_id')
        if user_id is None or recipe_id is None:
            return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # missing arguments
        like = Like(user_id=user_id, recipe_id=recipe_id)
        db.session.add(like)
        db.session.commit()
        information = response_builder(like, Like)
        return jsonify({'error_code': OK, 'result': information}), 201
    else:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200


@auto.doc()
@mod.route('/<int:id>', methods=['GET'])
@login_required
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
@mod.route('/<int:id>', methods=['DELETE'])
@login_required
def delete_like(id):
    """
    Delete like.
    :param id: favorite id
    :return: json with parameters:
            error_code - server response_code
    """
    like = Like.query.get(id)
    if not like:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # like with `id` isn't exist
    if current_user.id == like.user_id:
        db.session.delete(like)
        db.session.commit()
        return jsonify({'error_code': OK}), 200
    else:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200