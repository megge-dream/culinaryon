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
    first_name_lang_en = db.Column(db.String(length=128), nullable=True)
    last_name = db.Column(db.String(length=128), nullable=True)
    last_name_lang_en = db.Column(db.String(length=128), nullable=True)
    work = db.Column(db.String(255), nullable=True)
    work_lang_en = db.Column(db.String(255), nullable=True)
    biography = db.Column(db.Text, nullable=True)
    biography_lang_en = db.Column(db.Text, nullable=True)
    quote = db.Column(db.Text, nullable=True)
    quote_lang_en = db.Column(db.Text, nullable=True)
    email = db.Column(db.String(250), nullable=False)
    main_photo = db.Column(db.Text, nullable=True)
    medium_photo = db.Column(db.Text, nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())

    # links
    photos = db.relationship(ChefPhoto, backref='chefs', lazy='select')
    recipes = db.relationship(Recipe, backref='chefs', lazy='select')

    def __unicode__(self):
        return self.first_name + ' ' + self.last_name
