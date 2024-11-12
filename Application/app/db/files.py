from datetime import datetime
from app.__init__ import db


class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(80), nullable=False)
    file_data = db.Column(db.LargeBinary(length=(2**24-1)), nullable=False) # Can save a file that is up to 16MB in size
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Extra
    ocr_status = db.Column(db.String(50), default="Pending")
    text_content = db.Column(db.Text, nullable=True)