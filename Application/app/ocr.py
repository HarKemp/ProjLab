from flask import Blueprint, url_for, redirect, render_template
from flask_login import login_required, current_user
from app.db.models import File, Invoice
from .ocr_utils import extract_text_from_pdf, get_ai_result, send_invoice

ocr = Blueprint('ocr', __name__)

@ocr.route('/convert-text/<int:file_id>', methods=['POST'])
@login_required
def convert_text(file_id):
    if file_id is None or not isinstance(file_id, int) or file_id < 1:
        print("NOK")
        return redirect(url_for('main.homepage'))
    else:
        print("OK")
        file = File.query.get(file_id)
        #Call OCR
        ocr_results = extract_text_from_pdf(file.file_data)
        ai_result = get_ai_result(ocr_results)
        #Save invoice into DB
        user_id = current_user.id
        send_invoice(ai_result,user_id)

        #     # Redirect to MyInvoices
        # TODO show message about convert status
        return redirect(url_for('ocr.my_invoices'))

@ocr.route('/my-invoices', methods=['GET'])
@login_required
def my_invoices():
    # Get all invoices by current user
    # pass the invoices invoices html
    user_id = current_user.id
    user_invoices = Invoice.query.filter_by(user_id=user_id).all()
    print(user_invoices)
    return render_template('invoices.html', invoices=user_invoices)


@ocr.route('/my-invoices/invoice/<int:invoice_id>', methods=['GET'])
@login_required
def invoice(invoice_id):
    if invoice_id is None or not isinstance(invoice_id, int) or invoice_id < 1:
        print("illegal invoice ID")
        return redirect(url_for('main.homepage'))
    else:
        user_id = current_user.id
        invoice = Invoice.query.filter_by(id=invoice_id, user_id=user_id).first()
        return render_template('invoice.html', invoice=invoice)

