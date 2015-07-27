from datetime import datetime

from app.api import db


class PromoCode(db.Model):
    """
    Need to add Table Structure
    """
    __tablename__ = "promo_codes"

    id = db.Column(db.Integer, primary_key=True)
    # number = db.Column(db.String, nullable=True)
    value = db.Column(db.String, default='')
    code = db.Column(db.String, default='')
    creation_date = db.Column(db.DateTime, default=datetime.utcnow())

    def __unicode__(self):
        return "%04d" % self.id + '-' + self.value + '-' + self.code