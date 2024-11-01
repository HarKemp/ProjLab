from flask import Blueprint, session, url_for, request, redirect, render_template
from flask_login import login_required
from app.db.models import File

ocr = Blueprint('ocr', __name__)

@ocr.route('/convert-text/<int:file_id>', methods=['POST'])
@login_required
def convert_text(file_id):
    # TODO make sure only owner can upload the file
    if file_id is None or not isinstance(file_id, int) or file_id < 1:
        print("NOK")
        return redirect(url_for('main.homepage'))
    else:
        print("OK")
        file = File.query.get(file_id)
        #     # Call ORC
        #     # Save invoice into DB
        #     # Redirect to MyInvoices
        return redirect(url_for('ocr.my_invoices'))

@ocr.route('/my_invoices', methods=['GET'])
@login_required
def my_invoices():
    print("Implement me")
    # Get all invoices by current user
    # pass the invoices invoices html
    return render_template("invoices.html")