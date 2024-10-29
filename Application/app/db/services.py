from app.__init__ import db


class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=False)
    units = db.Column(db.Float)
    emissions = db.relationship('Emission', backref='service', lazy=True)
    