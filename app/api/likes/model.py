from datetime import datetime

from app.api import db


class Like(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "likes"

    id = db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)

    def __unicode__(self):
        return unicode(self.id)


class LikeWine(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "likes_wines"

    id = db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    wine_id = db.Column(db.Integer, db.ForeignKey('wines.id'), nullable=False)

    def __unicode__(self):
        return unicode(self.id)