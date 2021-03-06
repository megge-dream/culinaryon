from datetime import datetime

from app.api import db
from app.api.basket.model import Basket


class Ingredient(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "ingredients"

    id = db.Column(db.Integer, primary_key=True)
    title_lang_ru = db.Column(db.String(250), nullable=False)
    title_lang_en = db.Column(db.String(250), nullable=True)
    amount = db.Column(db.Float, nullable=True, default=0)
    unit_lang_ru = db.Column(db.String(250), nullable=True)
    unit_lang_en = db.Column(db.String(250), nullable=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"))
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())

    baskets = db.relationship(Basket, backref='ingredients', lazy='dynamic')

    def __unicode__(self):
        return self.title_lang_ru