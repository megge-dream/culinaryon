from datetime import datetime

from app.api import db
from app.api.photos.model import ChefPhoto
from app.api.recipes.model import Recipe


class Chef(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "chefs"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(length=128), nullable=True)
    last_name = db.Column(db.String(length=128), nullable=True)
    work = db.Column(db.String(255), nullable=True)
    biography = db.Column(db.Text, nullable=True)
    quote = db.Column(db.Text, nullable=True)
    email = db.Column(db.String(250), nullable=False)
    main_photo = db.Column(db.Text, nullable=False)
    medium_photo = db.Column(db.Text, nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())

    # links
    all_photos = db.relationship(ChefPhoto, backref='chefs', lazy='dynamic')
    recipes = db.relationship(Recipe, backref='chefs', lazy='dynamic')
