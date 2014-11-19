from datetime import datetime

from app.api import db


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