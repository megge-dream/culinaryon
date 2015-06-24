from datetime import datetime

from app.api import db


class Wine(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "wines"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())
    country = db.Column(db.String(250), nullable=True)
    region = db.Column(db.String(250), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    type_of_grape = db.Column(db.String(250), nullable=True)
    parker_points = db.Column(db.Integer, nullable=True)

    def __unicode__(self):
        return self.title