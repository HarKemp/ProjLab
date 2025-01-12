# This file holds a table that gets populated when app is launched
# It holds the service category and emission value per 1 unit

import csv
from app.__init__ import db

class EmissionValue(db.Model):
    __tablename__ = 'emission_categories'
    name = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<EmissionValue name={self.name}, coefficient={self.coefficient}>"

# inits table with starting values in for CO2 emissions
def create_and_populate_table(app, csv_file_path):
    with app.app_context():

        # Read the CSV and insert values
        with open(csv_file_path, encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Strip any unwanted spaces from the header keys
                name = row['name'].strip().lower()
                value = float(row['value'].strip())
                # Check for duplicates before inserting
                if not EmissionValue.query.filter_by(name=name).first():
                    category = EmissionValue(name=name, value=value)
                    db.session.add(category)

        db.session.commit()
        print("Emission Value Table populated successfully!")

# Finds value in db by getting the name from invoice
def get_emission_value(name):
    # Search for names that contain the search term, case-insensitive
    if not name:
        return 1.0
    result = EmissionValue.query.filter(EmissionValue.name.ilike(f'%{name.lower()}%')).first()
    return result.value if result else 0
