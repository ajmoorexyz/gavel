from gavel.models import db
import gavel.utils as utils
import gavel.crowd_bt as crowd_bt
from sqlalchemy.orm.exc import NoResultFound

ignore_table = db.Table('ignore',
    db.Column('annotator_id', db.Integer, db.ForeignKey('annotator.id')),
    db.Column('item_id', db.Integer, db.ForeignKey('item.id'))
)

class Annotator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120))
    active = db.Column(db.Boolean, default=True)
    description = db.Column(db.Text)
    secret = db.Column(db.String(32), unique=True, nullable=False)
    next_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    next = db.relationship('Item', foreign_keys=[next_id], uselist=False)
    prev_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    prev = db.relationship('Item', foreign_keys=[prev_id], uselist=False)
    ignore = db.relationship('Item', secondary=ignore_table)

    alpha = db.Column(db.Float)
    beta = db.Column(db.Float)

    def __init__(self, name, email, description):
        self.name = name
        self.email = email
        self.description = description
        self.alpha = crowd_bt.ALPHA_PRIOR
        self.beta = crowd_bt.BETA_PRIOR
        self.secret = utils.gen_secret(32)

    @classmethod
    def by_secret(cls, secret):
        try:
            annotator = cls.query.filter(cls.secret == secret).one()
        except NoResultFound:
            annotator = None
        return annotator

    @classmethod
    def by_id(cls, uid):
        if uid is None:
            return None
        try:
            annotator = cls.query.with_for_update().get(uid)
        except NoResultFound:
            annotator = None
        return annotator