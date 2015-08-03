from datetime import datetime

from app.api import db


class SchoolEvent(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "schoolEvents"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'))
    description = db.Column(db.Text, nullable=True)
    description_lang_en = db.Column(db.Text, nullable=True)
    url = db.Column(db.Text, nullable=True)
    places_all = db.Column(db.Integer, nullable=False)
    places_left = db.Column(db.Integer, nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())

    def __unicode__(self):
        return str(self.id)