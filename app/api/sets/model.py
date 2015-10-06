from datetime import datetime

from app.api import db
from app.api.users.constants import MONTH
from app.api.recipes.model import Recipe


class UserSet(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "users_sets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    set_id = db.Column(db.Integer(), db.ForeignKey('sets.id'))
    open_date = db.Column(db.DateTime, default=datetime.utcnow())
    open_type = db.Column(db.Integer(), default=MONTH)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())

    def __unicode__(self):
        return self.id


class Set(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "sets"

    id = db.Column(db.Integer, primary_key=True)
    title_lang_ru = db.Column(db.String(250), nullable=False)
    title_lang_en = db.Column(db.String(250), nullable=True)
    photo = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=True)
    store_id = db.Column(db.String(250), nullable=True)
    sale_store_id = db.Column(db.String(250), nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())

    user_sets = db.relationship(UserSet, backref='sets', lazy='dynamic')
    recipes = db.relationship(Recipe, backref='sets', lazy='select')

    def __unicode__(self):
        return self.title_lang_ru