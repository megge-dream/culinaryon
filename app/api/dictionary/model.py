from datetime import datetime

from app.api import db


class Dictionary(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "dictionary"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    description = db.Column(db.Text, nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())

    def __unicode__(self):
        return self.title