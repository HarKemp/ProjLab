from app.__init__ import db
from datetime import datetime
from .invoices_services import invoices_services


class Invoice(db.Model):
    #TODO rework this based on excel "Invoices" in docs
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=False)
    issuer = db.Column(db.String(80), nullable=False)
    issuer_registration_number = db.Column(db.String(64), nullable=False)
    issuer_address = db.Column(db.String(128), nullable=False)
    receiver = db.Column(db.String(80), nullable=False)
    receiver_registration_number = db.Column(db.String(64), nullable=False)
    receiver_address = db.Column(db.String(128), nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    issue_number = db.Column(db.String(80), nullable=False)
    # TODO: sum_total with currency separator as str, or sum_total as float with currency elsewhere
    sum_total = db.Column(db.String(15), nullable=False)
    services = db.relationship('Service', secondary=invoices_services, backref=db.backref('invoice', lazy='dynamic'))
    file = db.relationship('File', backref='invoice', uselist=False)

    @property
    def total_emissions(self):
        """Calculate the total emission value of all services related to this invoice."""
        total_emissions = 0.0
        for service in self.services:
            total_emissions += service.total_emissions
        return total_emissions
