import cgi

from flask.ext.login import login_required
from flask_mail import Message
from flask.ext.oauthlib.client import OAuthException
from flask import request, jsonify, Blueprint, redirect
from flask.ext.login import login_user
from sqlalchemy import and_

from app.api import vkontakte, mail
from app.api.chefs.views_v2 import chef_response_builder
from app.api.constants import BAD_REQUEST, OK
from app.api import auto, twitter
from app.api.helpers import *
from app.api.recipes.views_v2 import recipe_response_builder
from app.api.users.constants import TW, FB, VK, APP_MAIL
from app.api.users.model import *
from app.decorators import admin_required


mod = Blueprint('users_v2', __name__, url_prefix='/api_v2')


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

    school_events = []
    for school_event in user.school_events:
        school_events.append(school_event.id)
    information['school_events'] = []
    if school_events is not None:
        for school_event_id in school_events:
            school_event = SchoolEvent.query.get(school_event_id)
            school_event_information = response_builder(school_event, SchoolEvent)
            information["school_events"].append(school_event_information)

    return jsonify({'error_code': OK, 'result': information}), 200


@auto.doc()
@mod.route('/users/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(id):
    """
    Delete user. (for admin users only)
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
def send_mail(chef_id):
    """
    Send mail to chef. List of parameters in json request:
            name (required)
            email (required)
            message_body (required)
    Example of request:
            {"name":"Alex", "email":"ria6@yandex.ru", "message_body":"good"}
    :param chef_id: chef id
    :return: json with parameters:
            error_code - server response_code
    """
    name = request.json.get('name')
    email_from = request.json.get('email')
    message_body = request.json.get('message_body')
    if name is None or message_body is None or email_from is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200
    if Chef.query.get(chef_id).email == "" or Chef.query.get(chef_id).email is None:
        msg = Message('From app Culinaryon',
                      sender=email_from,
                      recipients=APP_MAIL)
    else:
        msg = Message('From app Culinaryon',
                      sender=email_from,
                      recipients=[APP_MAIL])
    msg.body = Chef.query.get(chef_id).first_name + " " + \
               Chef.query.get(chef_id).last_name + \
               " receive a message from " + name + ": \n" + cgi.escape(message_body) + "\nResponse to " + email_from
    mail.send(msg)
    return jsonify({'error_code': OK}), 200


@auto.doc()
@mod.route('/send_report/', methods=['POST'])
@login_required
def send_report():
    """
    Send report to admin. List of parameters in json request:
            message_body (required)
            email (required)
    Example of request:
            {"message_body":"good", "email":"ria6@yandex.ru"}
    :return: json with parameters:
            error_code - server response_code
    """
    message_body = request.json.get('message_body')
    email_from = request.json.get('email')
    if message_body is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200
    report = Report(user_id=current_user.id, message_body=message_body)
    db.session.add(report)
    db.session.commit()
    msg = Message('From app Culinaryon',
                  sender=email_from,
                  recipients=[APP_MAIL])
    msg.body = "Report from " + email_from + ": \n" + cgi.escape(message_body)
    mail.send(msg)
    return jsonify({'error_code': OK}), 200


@auto.doc()
@mod.route('/forget/', methods=['POST'])
def forget_password():
    """
    Send password in email to user. List of parameters in json request:
            email (required)
    Example of request:
            {"email":"ria6@yandex.ru"}
    :return: json with parameters:
            error_code - server response_code
    """
    user_email = request.json.get('email')
    if user_email is None or User.query.filter_by(email=user_email).all() is None:
        return jsonify({'error_code': BAD_REQUEST, 'result': 'not ok'}), 200
    msg = Message('From app Culinaryon',
                  sender=APP_MAIL,
                  recipients=[user_email])
    message_body = ""
    msg.body = "Your password is " + cgi.escape(message_body)
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
        return jsonify({'error_code': OK, 'user': response_builder(user, User), 'access_token': user.get_auth_token()})
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
    # return jsonify({'error_code': 0, 'result': "already authorized",
    # 'access_token': current_user.get_auth_token()})

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
                    return jsonify({'error_code': OK, 'user': response_builder(user, User),
                                    'access_token': user.get_auth_token()})
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
                    return jsonify({'error_code': OK, 'user': response_builder(new_user, User),
                                    'access_token': new_user.get_auth_token()})
                else:
                    return jsonify({'error_code': BAD_REQUEST, 'result': 'Cant Login user via twitter'}), 200

        except Exception as e:
            return jsonify({'error_code': BAD_REQUEST, 'result': str(e)}), 200


@auto.doc()
@mod.route('/login/facebook', methods=['POST'])
def facebook_login():
    """
    Authorization through Facebook SDK.
    If a user's successfully logged on Facebook (via SDK), get user's facebook account information:
    `email`, `first_name`, `last_name` and facebook `user_id`.

    :return: if something went wrong, return `error_code` <> 0,
    if new user created and login, then return {error_code: 0, result: <user info>, access_token: <token>}
    if user has existed then just return {error_code: 0, user_id: <user_id>, access_token: <token>}
    """
    facebook_user_id = request.json.get('user_id')
    email = request.json.get('email')
    first_name = request.json.get('first_name')
    last_name = request.json.get('last_name')
    if email is None or facebook_user_id is None or first_name is None or last_name is None:
        return jsonify({'error_code': BAD_REQUEST,
                        'result': 'Missed arguments.'
                                  'You should provide facebook `user_id`, `first_name`,'
                                  '`last_name` and `email`'}), 200  # missing arguments

    user = user_exist(provider_user_id=facebook_user_id, provider_id=FB)
    if user:
        # User exists
        update_time = datetime.utcnow()
        user.last_login_at = update_time
        if login_user(user):
            connection = Connection(user_id=user.id, provider_id=FB, provider_user_id=facebook_user_id,
                                    access_token="", creation_date=update_time)
            db.session.add(connection)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            db.session.commit()
            return jsonify({'error_code': OK, 'user': response_builder(user, User),
                            'access_token': user.get_auth_token()})
        else:
            return jsonify({'error_code': BAD_REQUEST, 'result': 'Something went wrong'}), 200
    else:
        # create New User
        update_time = datetime.utcnow()
        new_user = User(last_login_at=update_time, registered_on=update_time, provider_id=FB,
                        provider_user_id=facebook_user_id, first_name=first_name, last_name=last_name, email=email)
        db.session.add(new_user)
        db.session.commit()
        connection = Connection(user_id=new_user.id, provider_id=FB, provider_user_id=facebook_user_id,
                                access_token="", creation_date=update_time)
        db.session.add(connection)
        db.session.commit()
        if login_user(new_user):
            return jsonify({'error_code': OK, 'user': response_builder(new_user, User),
                            'access_token': new_user.get_auth_token()})
        else:
            return jsonify({'error_code': BAD_REQUEST, 'result': 'Cant Login user via fb'}), 200


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
    # return jsonify({'error_code': 0, 'result': "already authorized",
    # 'access_token': current_user.get_auth_token()})
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
            return jsonify(
                {'error_code': OK, 'user': response_builder(user, User), 'access_token': user.get_auth_token()})
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
            return jsonify({'error_code': OK, 'user': response_builder(new_user, User),
                            'access_token': new_user.get_auth_token()})
        else:
            return jsonify({'error_code': BAD_REQUEST, 'result': 'Cant Login user via VK.com'}), 200


@auto.doc()
@mod.route('/top/')
def get_top():
    """
    :return: 5 best:
    - chefs,
    - seminars,
    - recipes.
    """
    lang = request.args.get('lang', type=unicode, default=u'en')
    PLACES_IN_TOP = 5
    information = {}
    chefs = Chef.query.limit(PLACES_IN_TOP).all()
    information['chefs'] = []
    for chef in chefs:
        information['chefs'].append(chef_response_builder(chef, lang=lang))

    if current_user.is_authenticated() and current_user.role_code == 0:
        recipe_query = Recipe.query
    else:
        recipe_query = Recipe.query.filter_by(type=PUBLISHED)
    recipes = recipe_query.order_by(Recipe.num_likes.desc()).limit(PLACES_IN_TOP).all()
    information['recipes'] = []
    for recipe in recipes:
        information_of_recipe = recipe_response_builder(recipe, lang=lang)
        information_of_recipe['ingredients'] = get_ingredients_by_divisions(recipe.id, lang=lang)
        information['recipes'].append(information_of_recipe)

    seminars = SchoolEvent.query.order_by(SchoolEvent.date.desc()).limit(5).all()
    information['seminars'] = []
    for seminar in seminars:
        information['seminars'].append(response_builder(seminar, SchoolEvent, lang=lang))

    return jsonify({'error_code': OK, 'result': information})



@auto.doc()
@mod.route('/appstore/')
def to_appstore():
    """
    Redirect to AppStore.
    """
    return redirect('https://itunes.apple.com/us/app/culinaryon-lucsie-recepty/id971017562?l=ru&ls=1&mt=8', 302)


################
# Helpers      #
################
def user_exist(provider_user_id, provider_id=0):
    user = User.query.filter(and_(User.provider_id == provider_id, User.provider_user_id == provider_user_id)).first()
    if user is None:
        return False
    else:
        return user