from datetime import datetime
import time
from flask.ext.login import UserMixin
from itsdangerous import JSONWebSignatureSerializer as Serializer

from werkzeug.security import generate_password_hash, check_password_hash
from app.api import db, login_manager, app
from app.api.favorites.model import Favorite
from app.api.likes.model import Like
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
    expire_in = db.Column(db.DateTime())
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
    social_id = db.Column(db.Integer, nullable=True)
    _password = db.Column('password', db.String(64), nullable=True)

    def _get_password(self):
        return self._password

    def _set_password(self, password):
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
        # TODO: helper function datetime->timestamp

        return s.dumps({'id': self.id, 'last_login_at': time.mktime(self.last_login_at.timetuple())})

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
    likes = db.relationship(Like, backref='users', lazy='dynamic')
    favorites_recipes = db.relationship(Favorite, backref='users', lazy='dynamic')
    connections = db.relationship(Connection, backref='users', lazy='dynamic')


@login_manager.token_loader
def token_loader(token):
    s = Serializer(SECRET_KEY)
    try:
        data = s.loads(token)
    except Exception:
        # TODO: need to implement normal logging w/ except
        app.logger.error("TokenLoader: cannot loads from token")
        return None
    user = User.query.get(data['id'])
    if user is not None and user.last_login_at == datetime.fromtimestamp(data['last_login_at']):
        return user
    return None


@login_manager.user_loader
def load_user(userid):
    """
    Flask-Login user_loader callback.
    The user_loader function asks this function to get a User Object or return
    None based on the userid.
    The userid was stored in the session environment by Flask-Login.
    user_loader stores the returned User object in current_user during every
    flask request.
    """
    return User.get(userid)