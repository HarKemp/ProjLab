from app.__init__ import db
from datetime import datetime
from .services_emissions import services_emissions


class Invoices(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    issuer = db.Column(db.String(80), nullable=False)
    issuer_registration_number = db.Column(db.String(64), nullable=False)
    issuer_address = db.Column(db.String(128), nullable=False)
    receiver = db.Column(db.String(80), nullable=False)
    receiver_registration_number = db.Column(db.String(64), nullable=False)
    receiver_address = db.Column(db.String(128), nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    issue_number = db.Column(db.String(80), nullable=False)
    services = db.relationship('Emissions', secondary=services_emissions, backref=db.backref('invoices', lazy='dynamic'))
    sum_total = db.Column(db.Float, nullable=False)
    pvn = db.Column(db.Integer, nullable=False)
