from app.__init__ import db
from datetime import datetime
from .invoices_services import invoices_services

class Invoice(db.Model):
    #TODO rework this based on excel "Invoices" in docs
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=False)

    issuer = db.Column(db.String(80), nullable=True)
    issuer_registration_number = db.Column(db.String(64), nullable=True)
    issuer_address = db.Column(db.String(128), nullable=True)
    receiver = db.Column(db.String(80), nullable=True)
    receiver_registration_number = db.Column(db.String(64), nullable=True)
    receiver_address = db.Column(db.String(128), nullable=True)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    issue_number = db.Column(db.String(80), nullable=True)
    # TODO: sum_total with currency separator as str, or sum_total as float with currency elsewhere
    sum_total = db.Column(db.String(15), nullable=True)
    services = db.relationship('Service', secondary=invoices_services, backref=db.backref('invoice', lazy='dynamic'))
    file = db.relationship('File', backref='invoice', uselist=False)

    @property
    def total_emissions(self):
        """Calculate the total emission value of all services related to this invoice."""
        total_emissions = 0.0
        for service in self.services:
            total_emissions += service.total_emissions
        return total_emissions

    def delete(self):
        try:
            # Delete emissions and services in bulk to reduce commit overhead
            for service in self.services:
                # Delete associated emissions first
                db.session.delete(service.emission)

            # Now delete the services
            for service in self.services:
                db.session.delete(service)

            # Finally, delete the invoice itself
            db.session.delete(self)

            # Commit all deletions in a single transaction
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()  # Rollback if any error occurs
            print(f"Error deleting invoice: {e}")
            return False