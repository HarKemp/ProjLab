from app.__init__ import db

services_emissions = db.Table('services_emissions',
                             db.Column('invoice_id', db.Integer, db.ForeignKey('invoices.id'), primary_key=True),
                             db.Column('emission_id', db.Integer, db.ForeignKey('emissions.id'), primary_key=True)
                             )
