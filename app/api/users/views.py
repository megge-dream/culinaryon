from flask import request, jsonify, url_for, Blueprint, session
from flask.ext.login import login_required, current_user, login_user
from flask_mail import Message
from flask.ext.oauthlib.client import OAuthException
from flask import request, jsonify, g, url_for, Blueprint, redirect, Flask, abort, render_template, flash
from flask.ext.login import current_user, login_user, logout_user
from sqlalchemy import and_
from wtforms import ValidationError

from app.api import facebook, vkontakte, mail
from app.api.constants import BAD_REQUEST, OK
from app.api import auto, twitter
from app.api.helpers import *
from app.api.users.constants import TW, FB, VK
from app.api.users.model import *
from app.decorators import admin_required


mod = Blueprint('users', __name__, url_prefix='/api')


# @mod.route('/admin_login', methods=['GET', 'POST'])
# def login():
#     out = {}
#     if current_user.is_authenticated():
#         return redirect(url_for('index'))
#     form = LoginForm()
#     try:
#         if form.validate_on_submit():
#             login_user(User.query.filter_by(email=form.email.data).first(), remember=True)
#             flash(u"Success login.", category='success')
#             out.update({'current_user': current_user})
#             return redirect(url_for('__init__.index'))
#     except ValidationError as v:
#         flash(v.message, category='error')
#     return render_template("login.html", form=form)


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
    user = User(email=email, password=password, first_name=first_name,
                last_name=last_name, last_login_at=datetime.utcnow())
    db.session.add(user)
    db.session.commit()
    login_user(user, remember=True)
    information = response_builder(user, User, excluded=['password'])
    return (jsonify({'error_code': OK, 'result': information}), 201,
            {'Location': url_for('.get_user', id=user.id, _external=True)})


@auto.doc()
@mod.route('/users/<int:id>', methods=['PUT'])
@login_required
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
    if current_user.id == id:
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
    else:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200


@auto.doc()
@mod.route('/users/', methods=['GET'])
@login_required
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
@login_required
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
    print(user)
    information = response_builder(user, User, excluded=['password'])
    return jsonify({'error_code': OK, 'result': information}), 200


# User can delete only himself.
@auto.doc()
@mod.route('/users/<int:id>', methods=['DELETE'])
@login_required
@admin_required
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


@auto.doc()
@mod.route('/send_mail/<int:chef_id>', methods=['POST'])
# @login_required
def send_mail(chef_id):
    """
    Send mail to chef. List of parameters in json request:
            message_body (required)
    Example of request:
            {"message_body":"good"}
    :param chef_id: chef id
    :return: json with parameters:
            error_code - server response_code
    """
    message_body = request.json.get('message_body')
    if message_body is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200
    msg = Message('From app Culinaryon',
                  sender='ria6@yandex.ru',
                  # sender=current_user.email,
                  recipients=[Chef.query.get(chef_id).email])
    msg.body = message_body
    mail.send(msg)
    return jsonify({'error_code': OK}), 200


@auto.doc()
@mod.route('/login', methods=['POST'])
def pure_login():
    """
    Pure auth. You should send email + password

    :return: if something went wrong, return `error_code` <> 0,
    Otherwise, return {error_code: 0, user_id: <user_id>, access_token: <token>}
    """
    email = request.json.get('email')
    password = request.json.get('password')
    if not email or not password:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'Email and password fields are required'}), 200

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'No user with such email'}), 200
    if user.check_password(password):
        return jsonify({'error_code': OK, 'user_id': user.id, 'access_token': user.get_auth_token()})
    else:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'Wrong password'})




@auto.doc()
@mod.route('/login/twitter')
def twitter_login():
    """
    Auth through twitter. Need to open webView

    :return: if something went wrong, return `error_code` <> 0,
    if new user created and login, then return {error_code: 0, result: <user info>, access_token: <token>}
    if user has existed then just return {error_code: 0, user_id: <user_id>, access_token: <token>}
    """
    # if current_user.is_authenticated():
    #     return jsonify({'error_code': 0, 'result': "already authorized",
    #                       'access_token': current_user.get_auth_token()})

    callback_url = url_for('.twitter_authorized')
    return twitter.authorize(callback=callback_url)


@mod.route('/login/twitter/oauthorized')
def twitter_authorized():
    resp = twitter.authorized_response()

    if resp is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'Twitter went wrong :)'}), 200
    else:
        try:
            user_id = resp['user_id']
            oauth_token = resp['oauth_token']
            oauth_token_secret = resp['oauth_token_secret']
            user = user_exist(provider_user_id=user_id, provider_id=TW)

            if user:
                # user exist
                # try to login
                update_time = datetime.utcnow()
                user.last_login_at = update_time
                if login_user(user):
                    connection = Connection(user_id=user.id, provider_id=TW, provider_user_id=user_id,
                                            access_token=oauth_token, creation_date=update_time)
                    db.session.add(connection)
                    db.session.commit()
                    return jsonify({'error_code': OK, 'user_id': user.id, 'access_token': user.get_auth_token()})
                else:
                    return jsonify({'error_code': BAD_REQUEST, 'result': 'Cant Login user'}), 200
            else:
                # create New User
                update_time = datetime.utcnow()
                new_user = User(last_login_at=update_time, registered_on=update_time, provider_id=TW,
                            provider_user_id=user_id)
                db.session.add(new_user)
                db.session.commit()

                connection = Connection(user_id=new_user.id, provider_id=TW, provider_user_id=user_id,
                                        access_token=oauth_token, creation_date=update_time)
                db.session.add(connection)
                db.session.commit()
                if login_user(new_user):
                    return jsonify({'error_code': OK, 'user_id': new_user.id,
                                    'access_token': new_user.get_auth_token()})
                else:
                    return jsonify({'error_code': BAD_REQUEST, 'result': 'Cant Login user via twitter'}), 200

        except Exception as e:
            return jsonify({'error_code': BAD_REQUEST, 'result': str(e)}), 200


@auto.doc()
@mod.route('/login/facebook')
def facebook_login():
    """
    Auth through the Facebook. Need to open webView

    :return: if something went wrong, return `error_code` <> 0,
    if new user created and login, then return {error_code: 0, result: <user info>, access_token: <token>}
    if user has existed then just return {error_code: 0, user_id: <user_id>, access_token: <token>}
    """
    # if current_user.is_authenticated():
    #     return jsonify({'error_code': 0, 'result': "already authorized",
    #                       'access_token': current_user.get_auth_token()})

    callback_url = url_for('.facebook_authorized', _external=True)
    return facebook.authorize(callback=callback_url)


@mod.route('/login/facebook/authorized')
def facebook_authorized():
    resp = facebook.authorized_response()
    if resp is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': request.args['error_reason']})
    if isinstance(resp, OAuthException):
        return jsonify({'error_code': BAD_REQUEST, 'result': resp.message})

    oauth_token = (resp['access_token'], '')
    session['oauth_token'] = oauth_token
    me = facebook.get('/me')

    user_id = me.data['id']
    user = user_exist(provider_user_id=user_id, provider_id=FB)
    if user:
        # user exist
        # try to login
        update_time = datetime.utcnow()
        user.last_login_at = update_time
        if login_user(user):
            connection = Connection(user_id=user.id, provider_id=FB, provider_user_id=user_id,
                                    access_token=str(oauth_token), creation_date=update_time)
            db.session.add(connection)
            db.session.commit()
            return jsonify({'error_code': OK, 'user_id': user.id, 'access_token': user.get_auth_token()})
        else:
            return jsonify({'error_code': BAD_REQUEST, 'result': 'Cant Login user via facebook'}), 200
    else:
        # create New User
        update_time = datetime.utcnow()
        new_user = User(last_login_at=update_time, registered_on=update_time, provider_id=FB,
                    provider_user_id=user_id)
        db.session.add(new_user)
        db.session.commit()
        connection = Connection(user_id=new_user.id, provider_id=FB, provider_user_id=user_id,
                                access_token=oauth_token, creation_date=update_time)
        db.session.add(connection)
        db.session.commit()
        if login_user(new_user):
            return jsonify({'error_code': OK, 'user_id': new_user.id, 'access_token': new_user.get_auth_token()})
        else:
            return jsonify({'error_code': BAD_REQUEST, 'result': 'Cant Login user via fb'}), 200


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')


@auto.doc()
@mod.route('/login/vkontakte')
def vkontakte_login():
    """
    Auth through VK.COM. Need to open webView

    :return: if something went wrong, return `error_code` <> 0,
    if new user created and login, then return {error_code: 0, result: <user info>, access_token: <token>}
    if user has existed then just return {error_code: 0, user_id: <user_id>, access_token: <token>}
    """
    # if current_user.is_authenticated():
    #     return jsonify({'error_code': 0, 'result': "already authorized",
    #                       'access_token': current_user.get_auth_token()})
    callback_url = url_for('.vkontakte_authorized', _external=True)
    return vkontakte.authorize(callback=callback_url)


@mod.route('/login/vkontakte/authorized')
def vkontakte_authorized():
    resp = vkontakte.authorized_response()
    if resp is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': request.args['error_reason']})
    if isinstance(resp, OAuthException):
        return jsonify({'error_code': BAD_REQUEST, 'result': resp.message})

    user_id = resp['user_id']
    oauth_token = resp['access_token']
    expires_in = resp['expires_in']

    user = user_exist(provider_user_id=int(user_id), provider_id=VK)
    if user:
        # user exist
        # try to login
        update_time = datetime.utcnow()
        user.last_login_at = update_time
        if login_user(user):
            connection = Connection(user_id=user.id, provider_id=VK, provider_user_id=int(user_id),
                                    access_token=oauth_token[0], expire_in=expires_in, creation_date=update_time)
            db.session.add(connection)
            db.session.commit()
            return jsonify({'error_code': OK, 'user_id': user.id, 'access_token': user.get_auth_token()})
        else:
            return jsonify({'error_code': BAD_REQUEST, 'result': 'Cant Login user via VK.com'}), 200
    else:
        # create New User
        update_time = datetime.utcnow()
        new_user = User(last_login_at=update_time, registered_on=update_time, provider_id=VK,
                    provider_user_id=user_id)
        db.session.add(new_user)
        db.session.commit()
        connection = Connection(user_id=new_user.id, provider_id=VK, provider_user_id=int(user_id),
                                access_token=oauth_token[0], creation_date=update_time)
        db.session.add(connection)
        db.session.commit()
        if login_user(new_user):
            return jsonify({'error_code': OK, 'user_id': new_user.id, 'access_token': new_user.get_auth_token()})
        else:
            return jsonify({'error_code': BAD_REQUEST, 'result': 'Cant Login user via VK.com'}), 200


################
# Helpers      #
################
def user_exist(provider_user_id, provider_id=0):
    user = User.query.filter(and_(User.provider_id == provider_id, User.provider_user_id == provider_user_id)).first()
    if user is None:
        return False
    else:
        return user