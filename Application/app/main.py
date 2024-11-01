from flask import Blueprint, render_template, url_for, request, redirect, session
from flask_login import login_required

from .utils import file_upload, file_download

main = Blueprint('main',__name__)

@main.route('/')
def index():
    return render_template("login.html")

@main.route("/homepage", methods=['GET', 'POST'])
@login_required
def homepage():
    if request.method == 'POST':
            if file_upload():
                file_uploaded = 'file_id' in session
                file_id = session.get('file_id')
                print(file_id)
                session['file_uploaded'] = file_uploaded
                return redirect(url_for('main.homepage'))
            else:
                return redirect(request.url)
    file_uploaded = session.pop('file_uploaded', False)
    file_id = session.pop('file_id')
    return render_template("homepage.html", file_uploaded=file_uploaded, file_id=file_id)

@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_page():
    if request.method == 'POST':
        if file_upload():
            # Check if a file has been uploaded by checking session
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

@main.route("/chart", methods=['GET', 'POST'])
@login_required
def chart():
    return render_template("chart.html")