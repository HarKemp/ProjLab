from app.__init__ import db
import re


class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.String(20)) # Supports 3 char currency + 2 decimal + 1 separator + 14 digits
    amount = db.Column(db.String(25),nullable=False) # Less excessive length
    emission = db.relationship('Emission', backref='service', uselist=False)

    @property
    def amount_value(self):
        """Extract numerical value from amount string"""
        match = re.search(r"[-+]?\d*\.\d+|\d+", self.amount)
        return float(match.group()) if match else 1.0

    @property
    def total_emissions(self):
        """Calculate total emissions using amount_value"""
        return self.amount_value * self.emission.value
