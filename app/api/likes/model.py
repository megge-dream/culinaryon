from datetime import datetime

from app.api import db


class Like(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "likes"

    id = db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'))

    def __unicode__(self):
        return unicode(self.id)


