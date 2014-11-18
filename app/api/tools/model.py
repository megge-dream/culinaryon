from datetime import datetime

from app.api import db
from app.api.photos.model import ToolPhoto


class Tool(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "tools"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250))
    description = db.Column(db.Text, nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())

    # links
    photo = db.relationship(ToolPhoto, backref='tools', lazy='dynamic')