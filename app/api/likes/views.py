from flask import Blueprint, jsonify, request

from app.api import db
from app.api.helpers import response_builder
from app.api.likes.model import Like
from app.api.users.model import User


mod = Blueprint('likes', __name__, url_prefix='/api/likes')


# {"user_id":3, "recipe_id":2}
@mod.route('/', methods=['POST'])
def new_like():
    user_id = request.json.get('user_id')
    recipe_id = request.json.get('recipe_id')
    if user_id is None or recipe_id is None:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # missing arguments
    like = Like(user_id=user_id, recipe_id=recipe_id)
    db.session.add(like)
    db.session.commit()
    information = response_builder(like, Like)
    return jsonify({'error_code': 201, 'result': information}), 201


@mod.route('/<int:id>', methods=['GET'])
def get_likes(id):
    liked_users = []
    amount = Like.query.filter_by(recipe_id=id).count()
    for like in Like.query.filter_by(recipe_id=id):
        information = response_builder(User.query.get(like.user_id), User, excluded=['password'])
        liked_users.append(information)
    return jsonify({'error_code': 200, 'amount': amount, 'users': liked_users}), 200


@mod.route('/<int:id>', methods=['DELETE'])
def delete_like(id):
    like = Like.query.get(id)
    if not like:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # like with `id` isn't exist
    db.session.delete(like)
    db.session.commit()
    return jsonify({'error_code': 200}), 200