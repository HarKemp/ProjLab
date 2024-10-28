from app.__init__ import db


class Emissions(db.Model):
    __tablename__ = 'emissions'
    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String(80), nullable=False)
    service_price = db.Column(db.Float, nullable=False)
    units_per_service = db.Column(db.Float)
    value = db.Column(db.Float, nullable=False)
    