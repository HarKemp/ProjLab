from app.__init__ import db

invoices_services = db.Table('invoices_services',
                             db.Column('invoice_id', db.Integer, db.ForeignKey('invoices.id'), primary_key=True),
                             db.Column('service_id', db.Integer, db.ForeignKey('services.id'), primary_key=True)
                             )
