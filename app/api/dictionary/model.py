from datetime import datetime

from app.api import db


class Dictionary(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "dictionary"

    id = db.Column(db.Integer, primary_key=True)
    title_lang_ru = db.Column(db.String(250), nullable=False)
    title_lang_en = db.Column(db.String(250), nullable=True)
    description_lang_ru = db.Column(db.Text, nullable=True)
    description_lang_en = db.Column(db.Text, nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())

    def __unicode__(self):
        return self.title_lang_ru