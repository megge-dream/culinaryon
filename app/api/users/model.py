from datetime import datetime
from flask.ext.login import UserMixin

from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from werkzeug.security import generate_password_hash, check_password_hash
from app.api import db, app
from app.api.favorites.model import Favorite
from app.api.likes.model import Like
from app.api.users.constants import USER, USER_ROLE, ADMIN, ACTIVE, USER_STATUS


class Connection(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "connections"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    provider_id = db.Column(db.Integer)
    prv_user_id = db.Column(db.Integer)
    a_token = db.Column(db.Text)
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
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer)
    registered_on = db.Column(db.DateTime, default=datetime.utcnow())
    provider_id = db.Column(db.Integer, nullable=True)
    social_id = db.Column(db.Integer, nullable=True)
    _password = db.Column('password', db.String(64))

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


    # ================================================================
    role_code = db.Column(db.SmallInteger, default=USER, nullable=False)

    @property
    def role(self):
        return USER_ROLE[self.role_code]

    def is_admin(self):
        return self.role_code == ADMIN

    # ================================================================
    # One-to-many relationship between users and user_statuses.
    status_code = db.Column(db.SmallInteger, default=ACTIVE)

    @property
    def status(self):
        return USER_STATUS[self.status_code]


    # ================================================================
    # Class methods


    @classmethod
    def authenticate(cls, email, password):
        user = cls.query.filter(User.email == email).first()

        if user:
            authenticated = user.check_password(password)
        else:
            authenticated = False

        return user, authenticated

    @classmethod
    def search(cls, keywords):
        criteria = []
        for keyword in keywords.split():
            keyword = '%' + keyword + '%'
            criteria.append(db.or_(
                User.name.ilike(keyword),
                User.email.ilike(keyword),
            ))
        q = reduce(db.and_, criteria)
        return cls.query.filter(q)

    @classmethod
    def get_by_id(cls, user_id):
        return cls.query.filter_by(id=user_id).first_or_404()

    def check_name(self, name):
        return User.query.filter(db.and_(User.name == name, User.email != self.id)).count() == 0

    # links
    likes = db.relationship(Like, backref='users', lazy='dynamic')
    favorites_recipes = db.relationship(Favorite, backref='users', lazy='dynamic')
    connections = db.relationship(Connection, backref='users', lazy='dynamic')

