from flask import Blueprint, render_template, url_for, request, redirect, jsonify
from flask_login import login_required, current_user
from app.db.models import File
from app.__init__ import db

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
    invoices = File.query.filter_by(user_id=current_user.id).all()
    return render_template("invoices.html", invoices=invoices)

# Runs when requested by the client side (usually every 10 seconds when the specific webpage is open)
@main.route('/invoice-status', methods=['GET'])
@login_required
def invoice_status():
    # Obtain all invoices for current user
    invoices = File.query.filter_by(user_id=current_user.id).all()
    data = []
    # Send data about invoices in json format
    for inv in invoices:
        data.append({
            'id': inv.id,
            'title': inv.title,
            'ocr_status': inv.ocr_status,
        })
    return jsonify(data)

@main.route("/chart", methods=['GET', 'POST'])
@login_required
def chart():
    return render_template("chart.html")