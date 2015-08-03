from datetime import datetime

from app.api import db, Wine


class TypeOfGrape(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "type_of_grape"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    title_lang_en = db.Column(db.String(250), nullable=True)
    photo = db.Column(db.Text, nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())
    wines = db.relationship(Wine, backref='type_of_grape', lazy='select')

    def __unicode__(self):
        return self.title