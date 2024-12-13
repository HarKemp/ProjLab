from app.__init__ import db
import re


class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.String(10))
    amount = db.Column(db.String(100),nullable=False)
    emission = db.relationship('Emission', backref='service', uselist=False)

    @property
    def total_emissions(self):
        match = re.search(r"[-+]?\d*\.\d+|\d+", self.amount)
        if match:
            return float(match.group()) * self.emission.value
        else:
            return 1.0