from datetime import datetime

from app.api import db
from app.api.basket.model import Basket


class Ingredient(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "ingredients"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250))
    amount = db.Column(db.Integer)
    unit = db.Column(db.String(250))
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"))
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())

    baskets = db.relationship(Basket, backref='ingredients', lazy='dynamic')