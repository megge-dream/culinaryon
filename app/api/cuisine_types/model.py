from datetime import datetime

from app.api import db


class CuisineType(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "cuisineTypes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    title_lang_en = db.Column(db.String(250), nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())

    def __unicode__(self):
        return self.title