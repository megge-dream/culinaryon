from datetime import datetime
from flask import url_for
from flask.ext.admin.form import thumbgen_filename
from markupsafe import Markup

from app.api import db


class RecipePhoto(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "recipePhotos"

    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.Text, nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())
    item_id = db.Column(db.Integer, db.ForeignKey("recipes.id"))

    def __unicode__(self):
        return unicode(self.data) or u''


class ChefPhoto(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "chefPhotos"

    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.Text, nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())
    item_id = db.Column(db.Integer, db.ForeignKey("chefs.id"))

    def __unicode__(self):
        return unicode(self.data)


class SchoolPhoto(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "schoolPhotos"

    id = db.Column(db.Integer, primary_key=True)
    photo = db.Column(db.Text, nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())
    item_id = db.Column(db.Integer, db.ForeignKey("schools.id"))

    def __unicode__(self):
        return unicode(self.data)