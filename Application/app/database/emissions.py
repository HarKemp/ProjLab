from app.__init__ import db


class Emission(db.Model):
    __tablename__ = 'emissions'
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)
