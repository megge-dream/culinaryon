from datetime import datetime

from app.api import db
from app.api.photos.model import SchoolPhoto


class School(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "schools"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())

    #links
    photo = db.relationship(SchoolPhoto, backref='school', lazy='dynamic')


class SchoolItem(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "schoolItems"

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'))
    step_number = db.Column(db.Integer)
    description = db.Column(db.Text, nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())
    photo = db.Column(db.Text)