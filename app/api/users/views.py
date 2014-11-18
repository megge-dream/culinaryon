from flask import request, jsonify, g, url_for, Blueprint, redirect, Flask

from app.api import db, auth
from app.api.helpers import *

mod = Blueprint('users', __name__, url_prefix='/api')


@auth.verify_password
def verify_password(email_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(email_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(email=email_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


# need validate email ^(?("")("".+?""@)|(([0-9a-zA-Z]((\.(?!\.))|[-!#\$%&'\*\+/=\?\^`\{\}\|~\w])*)(?<=[0-9a-zA-Z])@))(?(\[)(\[(\d{1,3}\.){3}\d{1,3}\])|(([0-9a-zA-Z][-\w]*[0-9a-zA-Z]\.)+[a-zA-Z]{2,6}))$
# {"email": "admin@mail.ru", "password": "password"}
@mod.route('/users/', methods=['POST'])
def new_user():
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


@mod.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
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


@mod.route('/users/', methods=['GET'])
def get_all_users():
    users = []
    for user in User.query.all():
        information = response_builder(user, User, excluded=['password'])
        users.append(information)
    return jsonify({'error_code': 200, 'result': users}), 200


@mod.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200
    information = response_builder(user, User, excluded=['password'])
    return jsonify({'error_code': 200, 'result': information}), 200


# User can delete only himself.
@mod.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'error_code': 400, 'result': 'not ok'}), 200
    db.session.delete(user)
    db.session.commit()
    return jsonify({'error_code': 200}), 200


@mod.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})