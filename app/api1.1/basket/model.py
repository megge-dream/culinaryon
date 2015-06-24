from datetime import datetime

from app.api import db


class Basket(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "baskets"

    id = db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), nullable=False)
    amount = db.Column(db.Integer, default=0)
    is_to_buy = db.Column(db.Boolean, default=0)
    is_in_stock = db.Column(db.Boolean, default=0)

    def __unicode__(self):
        return unicode(self.id) or u''
