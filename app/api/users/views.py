from flask import request, jsonify, g, url_for, Blueprint, redirect, Flask, abort
from flask.ext.login import login_required, current_user, login_user, logout_user

from app.api import db, auto
from app.api.constants import BAD_REQUEST
from app.api.helpers import *
from app.api.users.model import *

mod = Blueprint('users', __name__, url_prefix='/api')


@auto.doc()
@mod.route('/users/', methods=['POST'])
def new_user():
    """
    Add new user. List of parameters in json request:
            email (required)
            password (required)
            first_name (optional)
            last_name (optional)
    Example of request:
            {"email": "admin@mail.ru", "password": "password"}
    :return: json with parameters:
            error_code - server response_code
            result - information about created user
    """
    email = request.json.get('email')
    password = request.json.get('password')
    first_name = request.json.get('first_name')
    last_name = request.json.get('last_name')
    if email is None or password is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # missing arguments
    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # existing user
    user = User(email=email, password=password, first_name=first_name, last_name=last_name, last_login_at=datetime.utcnow())
    db.session.add(user)
    db.session.commit()
    login_user(user, remember=True)
    information = response_builder(user, User, excluded=['password'])
    return (jsonify({'error_code': OK, 'result': information}), 201,
            {'Location': url_for('.get_user', id=user.id, _external=True)})

@auto.doc()
@mod.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    """
    Update exists user. List of parameters in json request:
            email (optional)
            password (optional)
            first_name (optional)
            last_name (optional)
    Example of request:
            {"email": "admin@mail.ru", "password": "password"}
    :param id: user id
    :return: json with parameters:
            error_code - server response_code
            result - information about updated user
    """
    user = User.query.get(id)
    if not user:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200
    if request.json.get('email'):
        user.email = request.json.get('email')
    if request.json.get('password'):
        password = request.json.get('password')
        user.hash_password(password)
    if request.json.get('first_name'):
        user.first_name = request.json.get('first_name')
    if request.json.get('last_name'):
        user.last_name = request.json.get('last_name')
    db.session.commit()
    user = User.query.get(id)
    information = response_builder(user, User, excluded=['password'])
    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/users/', methods=['GET'])
def get_all_users():
    """
    Get information about all exist users.
    :return: json with parameters:
            error_code - server response_code
            result - information about users
    """
    users = []
    for user in User.query.all():
        information = response_builder(user, User, excluded=['password'])
        users.append(information)
    return jsonify({'error_code': OK, 'result': users}), 200


@auto.doc()
@mod.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    """
    Get information about user.
    :param id: user id
    :return: json with parameters:
            error_code - server response_code
            result - information about user
    """
    user = User.query.get(id)
    if not user:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200
    information = response_builder(user, User, excluded=['password'])
    return jsonify({'error_code': OK, 'result': information}), 200


# User can delete only himself.
@auto.doc()
@mod.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    """
    Delete user.
    :param id: user id
    :return: json with parameters:
            error_code - server response_code
    """
    user = User.query.get(id)
    if not user:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200
    db.session.delete(user)
    db.session.commit()
    return jsonify({'error_code': OK}), 200


# @mod.route('/login', methods=['POST'])
# def log_in():
#     email = request.json.get('email')
#     password = request.json.get('password')
#     if email is None or password is None:
#         return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # missing arguments
#     if User.query.filter_by(email=email).first() is None:
#         return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200  # existing user
#     user = User.query.filter_by(email=email).first()
#     if not user.check_password(password):
#         return jsonify({'error_code': BAD_REQUEST, 'result': 'incorrect password'}), 200
#     information = response_builder(user, User, excluded=['password'])
#     return jsonify({'error_code': OK, 'result': information}), 200
#
#
# # {"access_token": "qwerty123", "social_id": 42, "social": "vk"}
# @mod.route('/login/provider', methods=['POST'])
# def provider_log_in():
#     access_token = request.json.get('access_token')
#     social_id = request.json.get('social_id')
#     expire_in = request.json.get('expire_in')
#     social = request.json.get('social')
#     provider_id = 0
#     if social == 'vk':
#         provider_id = 0
#     elif social == 'fb':
#         provider_id = 1
#     if Connection.query.filter_by(prv_user_id=social_id, provider_id=provider_id).first() is None:
#         user = User(social_id=social_id, provider_id=provider_id)
#         db.session.add(user)
#         db.session.commit()
#         user = User.query.filter_by(social_id=social_id, provider_id=provider_id).first()
#         connection = Connection(user_id=user.id, provider_id=provider_id, prv_user_id=social_id, a_token=access_token,
#                                 expire_in=expire_in)
#         db.session.add(connection)
#         db.session.commit()
#         return jsonify({'error_code': OK, 'result': 'user is created'}), 201
#     else:
#         user = User.query.filter_by(social_id=social_id, provider_id=provider_id).first()
#         user.social_id = social_id
#         user.provider_id = provider_id
#         user.last_login_at = datetime.utcnow()
#         db.session.commit()
#         connection = Connection.query.filter_by(provider_id=provider_id, prv_user_id=social_id)
#         connection.a_token = access_token
#         connection.expire_in = expire_in
#         return jsonify({'error_code': OK, 'result': 'user is updated'}), 201

@mod.route('/test/')
@login_required
def test():
    # if not current_user.is_authenticated:
    #     return jsonify(flag='bye'), 200
    user = current_user

    return jsonify(flag='true', userid=user.id), 200

@mod.route('/test1/')
@login_required
def test1():
    print(current_user.get_id())
    logout_user()
    return jsonify(flag='true', id=current_user.get_id())

