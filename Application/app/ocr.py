from flask import Blueprint, session, flash, url_for, request, redirect, render_template, jsonify
from flask_login import login_required, current_user
from app.db.models import File
from app.__init__ import db

ocr = Blueprint('ocr', __name__)

from app.tasks import ocr_task

# @ocr.route('/convert-text/<int:file_id>', methods=['POST'])
# @login_required
# def convert_text(file_id):
#     if file_id is None or not isinstance(file_id, int) or file_id < 1:
#         print("NOK")
#         return redirect(url_for('main.homepage'))
#     else:
#         print("OK")
#         file = File.query.get(file_id)
#         #     # Call ORC
#         #     # Save invoice into DB
#         #     # Redirect to MyInvoices
#         return redirect(url_for('ocr.my_invoices'))

@ocr.route('/convert-text/<int:file_id>', methods=['POST'])
@login_required
def convert_text(file_id):
    file = File.query.get(file_id)
    if file is None or file.user_id != current_user.id:
        flash("You do not have permission to access this file.", "alert-danger")
        return redirect(url_for('main.homepage'))

    # Set initial OCR status to "Pending" and save to the database
    file.ocr_status = "Pending"
    db.session.commit()

    # Queue the OCR task
    ocr_task.delay(file_id)
    # flash("OCR processing has started.", "alert-success")

    return redirect(url_for('ocr.my_invoices'))

@ocr.route('/my_invoices', methods=['GET'])
@login_required
def my_invoices():
    # Get all invoices by current user
    # pass the invoices invoices html
    invoices = File.query.filter_by(user_id=current_user.id).all()
    return render_template("invoices.html", invoices=invoices)

@ocr.route('/invoice-status', methods=['GET'])
@login_required
def invoice_status():
    invoices = File.query.filter_by(user_id=current_user.id).all()
    data = []
    for inv in invoices:
        data.append({
            'id': inv.id,
            'title': inv.title,
            'ocr_status': inv.ocr_status,
        })
    return jsonify(data)