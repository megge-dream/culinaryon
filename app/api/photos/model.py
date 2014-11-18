from datetime import datetime

from app.api import db


class RecipePhoto(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "recipePhotos"

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Text)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())
    item_id = db.Column(db.Integer, db.ForeignKey("recipes.id"))


class ChefPhoto(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "chefPhotos"

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Text)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())
    item_id = db.Column(db.Integer, db.ForeignKey("chefs.id"))


class ToolPhoto(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "toolPhotos"

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Text)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())
    item_id = db.Column(db.Integer, db.ForeignKey("tools.id"))


class SchoolPhoto(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "schoolPhotos"

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Text)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())
    item_id = db.Column(db.Integer, db.ForeignKey("schoolItems.id"))