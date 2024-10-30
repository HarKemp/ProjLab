from flask import Blueprint, session
from flask_login import login_required

from app.db.models import File

ocr = Blueprint('ocr', __name__)


@ocr.route('/convertText', methods=['POST'])
@login_required
def convert_text():
    file_id = session.get('file_id')
    file = File.query.get(file_id)
    print(file.title)
    print(file.upload_date)

    if file:
        file_data = file.read()
        # Call ORC
        # Save invoice into DB
        # Redirect to MyInvoices
        return "Converting " + file.title + "...", 200
    return "No file provided", 400
