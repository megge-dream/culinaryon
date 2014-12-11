import base64
from datetime import datetime
from flask.ext.login import UserMixin
from itsdangerous import JSONWebSignatureSerializer as Serializer

from werkzeug.security import generate_password_hash, check_password_hash
from app.api import db, login_manager, app
from app.api.favorites.model import Favorite
from app.api.likes.model import Like
from app.api.basket.model import Basket
from app.api.users.constants import USER, USER_ROLE, ADMIN, ACTIVE, USER_STATUS, NO_PROVIDER, PROVIDER_LIST
from config import SECRET_KEY


class Connection(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "connections"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    provider_id = db.Column(db.Integer)
    provider_user_id = db.Column(db.Integer)
    access_token = db.Column(db.Text)
    expire_in = db.Column(db.Integer())
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())


class User(db.Model, UserMixin):
    """
    Need to add Table Structure
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(length=250), nullable=True)
    first_name = db.Column(db.String(length=128), nullable=True)
    last_name = db.Column(db.String(length=128), nullable=True)
    active = db.Column(db.Boolean, default=1)
    last_login_at = db.Column(db.DateTime())
    registered_on = db.Column(db.DateTime, default=datetime.utcnow())
    provider_user_id = db.Column(db.Integer, nullable=True)

    _password = db.Column('password', db.String(64), nullable=True)

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        if password is not None:
            self._password = generate_password_hash(password)

    # Hide password encryption by exposing password field only.
    password = db.synonym('_password',
                          descriptor=property(_get_password,
                                              _set_password))

    def check_password(self, password):
        if self.password is None:
            return False
        return check_password_hash(self.password, password)

    # token-based auth implementation
    def get_auth_token(self):
        s = Serializer(SECRET_KEY)
        # TODO helper function datetime->timestamp

        # return s.dumps({'id': self.id, 'last_login_at': time.mktime(self.last_login_at.timetuple())})
        return s.dumps({'id': self.id})

    # ================================================================
    role_code = db.Column(db.SmallInteger, default=USER, nullable=False)

    @property
    def role(self):
        return USER_ROLE[self.role_code]

    def is_admin(self):
        return self.role_code == ADMIN

    # ================================================================
    provider_id = db.Column(db.Integer, nullable=True, default=NO_PROVIDER)

    @property
    def provider(self):
        return PROVIDER_LIST[self.provider_id]


    # ================================================================
    # One-to-many relationship between users and user_statuses.
    status_code = db.Column(db.SmallInteger, default=ACTIVE)

    @property
    def status(self):
        return USER_STATUS[self.status_code]

    # ================================================================
    # Class methods
    @staticmethod
    def get(userid):
        """
        Static method to search the database and see if userid exists.  If it
        does exist then return a User Object.  If not then return None as
        required by Flask-Login.
        """
        #For this example the USERS database is a list consisting of
        #(user,hased_password) of users.
        user = User.query.get(userid)
        if user is not None:
            return user
        return None


    # links
    likes = db.relationship(Like, backref='users', lazy='select')
    favorites_recipes = db.relationship(Favorite, backref='users', lazy='select')
    connections = db.relationship(Connection, backref='users', lazy='select')
    baskets = db.relationship(Basket, backref='users', lazy='select')

    def __unicode__(self):
        return self.email or unicode(self.id)


#@login_manager.token_loader
def token_loader(token):
    """
    this sets the callback for loading a user from an authentication
        token. The function you set should take an authentication token
        (a ``unicode``, as returned by a user's `get_auth_token` method) and
        return a user object, or ``None`` if the user does not exist.
    """
    s = Serializer(SECRET_KEY)
    try:
        data = s.loads(token)
    except Exception:
        # TODO need to implement normal logging w/ except
        app.logger.error("TokenLoader: cannot loads from token")
        return None
    user = User.query.get(data['id'])

    if user is not None and user.last_login_at == datetime.fromtimestamp(data['last_login_at']):
        return user
    return None


# @login_manager.user_loader
# def load_user(userid):
#     """
#     Flask-Login user_loader callback.
#     The user_loader function asks this function to get a User Object or return
#     None based on the userid.
#     The userid was stored in the session environment by Flask-Login.
#     user_loader stores the returned User object in current_user during every
#     flask request.
#     """
#     return User.get(userid)

@login_manager.request_loader
def load_user_from_header(request):

    # first, try to login using the api_key url arg
    access_token = request.args.get('access_token')
    if access_token:
        s = Serializer(SECRET_KEY)
        try:
            data = s.loads(access_token)
        except Exception:
            # TODO need to implement normal logging w/ except
            app.logger.error("TokenLoader: cannot loads from token")
            return None

        user = User.get(data['id'])
        #if user is not None and user.last_login_at == datetime.fromtimestamp(data['last_login_at']):
        if user:
            return user

    # next, try to login using Basic Auth
    access_token = request.headers.get('Authorization')
    if access_token:
        if access_token.startswith('Basic '):
            access_token = access_token.replace('Basic ', '', 1)
        try:
            access_token = base64.b64decode(access_token)
        except TypeError:
            pass

        s = Serializer(SECRET_KEY)
        try:
            data = s.loads(access_token)
        except Exception:
            # TODO need to implement normal logging w/ except
            app.logger.error("TokenLoader: cannot loads from token")
            return None

        user = User.get(data['id'])
        # if user is not None and user.last_login_at == datetime.fromtimestamp(data['last_login_at']):
        if user:
            return user
    # finally, return None if both methods did not login the user
    return None