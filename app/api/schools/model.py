from datetime import datetime

from app.api import db
from app.api.photos.model import SchoolPhoto


class SchoolItem(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "schoolItems"

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'))
    step_number = db.Column(db.Integer)
    description = db.Column(db.Text, nullable=True)
    description_lang_en = db.Column(db.Text, nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())
    photo = db.Column(db.Text)

    def __unicode__(self):
        return str(self.id)


class School(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "schools"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())

    #links
    photos = db.relationship(SchoolPhoto, backref='school', lazy='select')
    school_items = db.relationship(SchoolItem, backref='school', lazy='select')

    def __unicode__(self):
        return self.title
