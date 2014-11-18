from datetime import datetime

from app.api import db


class Category(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250))
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())
