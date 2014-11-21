from flask import request, jsonify, g, url_for, Blueprint, redirect, Flask, abort
from flask.ext.login import login_required, current_user

from app.api import db, auto
from app.api.helpers import *

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
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # missing arguments
    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200  # existing user
    user = User(email=email, first_name=first_name, last_name=last_name)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    information = response_builder(user, User, excluded=['password'])
    return (jsonify({'error_code': 200, 'result': information}), 201,
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
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200
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
    return jsonify({'error_code': 200, 'result': information}), 200


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
    return jsonify({'error_code': 200, 'result': users}), 200


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
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200
    information = response_builder(user, User, excluded=['password'])
    return jsonify({'error_code': 200, 'result': information}), 200


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
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200
    db.session.delete(user)
    db.session.commit()
    return jsonify({'error_code': 200}), 200


# TODO doc description of return
@auto.doc()
@mod.route('/token')
#@auth.login_required
def get_auth_token():
    """
    Get token for current user.
    :return: json with parameters:
            token -
            duration -
    """
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})

@mod.route('/test')
# @login_required
def test():
    # if not current_user.is_authenticated:
    #     return jsonify(flag='bye'), 200
    f = str(current_user.is_authenticated)
    return jsonify(flag=f),200