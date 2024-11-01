from flask import Blueprint, session, url_for, request, redirect
from flask_login import login_required

from app.db.models import File

ocr = Blueprint('ocr', __name__)


@ocr.route('/convert-text/<int:file_id>', methods=['POST'])
@login_required
def convert_text(file_id):

    if file_id is not None:
        return redirect(url_for('main.homepage'))
    else:
        file = File.query.get(file_id)
    #     # Call ORC
    #     # Save invoice into DB
    #     # Redirect to MyInvoices
        return "Converting " + file.title + "...", 200
