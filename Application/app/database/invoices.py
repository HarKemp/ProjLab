from app.__init__ import db
from datetime import datetime
from .invoices_services import invoices_services
import re

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

    def update(self, data):
        try:
            # Update invoice fields
            if 'fields' in data:
                for field in data['fields']:
                    key = field['key']
                    value = field['value']

                    # Skip non-editable fields
                    if key == 'total_emissions':
                        continue

                    # If the key is 'issue_date', convert the string to a correct date format
                    if key == 'issue_date':
                        value = datetime.strptime(value, '%Y-%m-%d').date()

                    # Update the invoice field if it exists in the model
                    if hasattr(self, key):
                        setattr(self, key, value)

            # Update services and associated emissions
            if 'services' in data:
                # Define field handlers - type safety and validation
                field_handlers = {
                    'name': lambda x: str(x),
                    'price': lambda x: str(x),  # Model is string
                    'amount': lambda x: str(x),  # Model is string
                    'emission': lambda x: float(x)  # Convert emissions to float
                }

                # Create a mapping of service IDs to their updates
                service_updates = {str(s['id']): s for s in data['services']}
                
                # Update all services in a single pass
                for service in self.services:
                    if str(service.id) in service_updates:
                        update_data = service_updates[str(service.id)]
                        
                        for field, handler in field_handlers.items():
                            if field in update_data:
                                try:
                                    # Validate the amount contains a number - can include non-numeric characters to designate electricity, etc.
                                    if field == 'amount':
                                        value = handler(update_data[field])
                                        # Just verify there is at least one number in the string
                                        if not re.search(r"[-+]?\d*\.?\d+", value):
                                            raise ValueError("Amount must contain at least one number")
                                        service.amount = value
                                    elif field == 'emission':
                                        try:
                                            value = handler(update_data[field])  # Convert emission to a float value
                                            if value < 0:
                                                raise ValueError("Emission value must be positive")
                                            service.emission.value = value
                                        except ValueError as e:
                                            print(f"Error updating emission for service {service.id}: {e}")
                                            continue
                                    else:
                                        setattr(service, field, handler(update_data[field]))
                                except (ValueError, TypeError) as e:
                                    print(f"Error updating {field} for service {service.id}: {e}")
                                    # On error - continue to the next field
                                    continue

            # Commit all changes to the database
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()  # Rollback if any error occurs
            print(f"Error updating invoice: {e}")
            return False