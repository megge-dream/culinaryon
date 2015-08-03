from datetime import datetime

from app.api import db

from app.api.favorites.model import FavoriteWine
from app.api.likes.model import LikeWine


class Wine(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "wines"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    title_lang_en = db.Column(db.String(250), nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())
    country = db.Column(db.String(250), nullable=True)
    country_lang_en = db.Column(db.String(250), nullable=True)
    region = db.Column(db.String(250), nullable=True)
    region_lang_en = db.Column(db.String(250), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    type_of_grape_id = db.Column(db.Integer, db.ForeignKey('type_of_grape.id'), nullable=True)
    parker_points = db.Column(db.Integer, nullable=True)
    photo = db.Column(db.Text, nullable=True)
    flag_photo = db.Column(db.Text, nullable=True)
    info = db.Column(db.Text, nullable=True)
    info_lang_en = db.Column(db.Text, nullable=True)

    favorites = db.relationship(FavoriteWine, backref='wines', cascade="all, delete-orphan", lazy='select')
    likes = db.relationship(LikeWine, backref='wines', cascade="all, delete-orphan", lazy='select')

    def __unicode__(self):
        return self.title