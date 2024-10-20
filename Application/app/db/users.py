from flask_login import UserMixin
from app.__init__ import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)
    # Only specific user will access the files in case something went wrong during upload
    files = db.relationship('File', backref='user', lazy=True)
