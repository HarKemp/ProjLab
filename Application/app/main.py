from flask import Blueprint, render_template, url_for, request, redirect, jsonify
from flask_login import login_required, current_user
from app.database.models import File, Invoice

from .utils import file_upload, file_download
from app.celery_tasks import ocr_task

main = Blueprint('main',__name__)

@main.route('/')
def index():
    return render_template("login.html")

@main.route("/homepage", methods=['GET', 'POST'])
@login_required
def homepage():
    if request.method == 'POST':
            if file_upload():
                return redirect(url_for('main.homepage'))
            else:
                return redirect(request.url)
    return render_template("homepage.html")

@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_page():
    if request.method == 'POST':
        if file_upload():
            return redirect(url_for('main.upload_page'))
        else:
            return redirect(request.url)

    return render_template('upload.html')

@main.route('/download', methods=['GET'])
@login_required
def download_page():
    return render_template('download.html')

@main.route('/download-file-<file_type>', methods=['GET'])
@login_required
def download_file(file_type):
    result = file_download(file_type)
    if not result:
        return redirect(url_for('main.download_page'))
    return result

@main.route('/my_invoices', methods=['GET'])
@login_required
def my_invoices():
    # Obtain all invoices for current user
    invoices = Invoice.query.filter_by(user_id=current_user.id).all()
    return render_template("invoices.html", invoices=invoices)

@main.route('/my-invoices/invoice/<int:invoice_id>', methods=['GET'])
@login_required
def invoice(invoice_id):
    if invoice_id is None or not isinstance(invoice_id, int) or invoice_id < 1:
        print("illegal invoice ID")
        return redirect(url_for('main.homepage'))
    else:
        user_id = current_user.id
        invoice = Invoice.query.filter_by(id=invoice_id, user_id=user_id).first()
        return render_template('invoice.html', invoice=invoice)

# Runs when requested by the client side (usually every 10 seconds when the specific webpage is open)
@main.route('/invoice-status', methods=['GET'])
@login_required
def invoice_status():
    # Obtain all invoices for current user
    invoices = Invoice.query.filter_by(user_id=current_user.id).all()
    data = []
    # Send data about invoices in json format
    for inv in invoices:
        data.append({
            'id': inv.id,
            'ocr_status': inv.file.ocr_status if inv.file else 'Error',
            'issuer': inv.issuer,
            'issuer_address': inv.issuer_address,
            'receiver': inv.receiver,
            'receiver_address': inv.receiver_address,
            'issue_number': inv.issue_number,
            'issue_date': inv.issue_date.strftime('%Y-%m-%d') if inv.issue_date else 'N/A',
            'sum_total': inv.sum_total,
            'services_count': len(inv.services),
            'total_emissions': inv.total_emissions,
            'issuer_registration_number': inv.issuer_registration_number,
            'receiver_registration_number': inv.receiver_registration_number,
        })
    return jsonify(data)

@main.route("/chart", methods=['GET', 'POST'])
@login_required
def chart():
    return render_template("chart.html")