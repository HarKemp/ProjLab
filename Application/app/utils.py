from flask import flash, request, current_app, send_from_directory, session
from flask_login import current_user
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from .database.models import File, User, Invoice
from app.__init__ import db
import pandas as pd
from datetime import datetime
import os

from app.celery_tasks import ocr_task


def file_upload():
    allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
    max_upload_size = current_app.config['MAX_UPLOAD_SIZE']
    upload_folder = current_app.config['UPLOAD_FOLDER']
    try:
        # Get list of all files selected
        files = request.files.getlist('files')
        # If no file is selected
        if not files or files[0].filename == '':
            flash('No file selected', 'alert-danger')
            return False

        file_ids = []

        for file in files:
            if file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                # flash(f'Invalid file format for {file.filename}', 'alert-danger')
                return False  # Stop processing
            # If file is allowed
            # Secure the filename and save it to the upload folder
            filename = secure_filename(file.filename)
            file_data = file.read()
            # Place copy of file in database
            file_id = insert_file_in_db(filename, file_data)
            file_ids.append(file_id)
            file.save(os.path.join(upload_folder, filename))
            flash(f"File uploaded successfully: {filename}", 'alert-success')

        # Start OCR celery task for each file
        for file_id in file_ids:
            file = File.query.get(file_id)
            if file:
                file.ocr_status = "Pending"
                new_invoice = Invoice(
                    user_id=session['user_id'],
                    file_id=file_id,
                    issuer="-",
                    issuer_registration_number="-",
                    issuer_address="-",
                    receiver="-",
                    receiver_registration_number="-",
                    receiver_address="-",
                    issue_date=None,
                    issue_number="-",
                    sum_total="-"
                )
                db.session.add(new_invoice)
                db.session.commit()
                ocr_task.delay(file_id)
        return True

    except RequestEntityTooLarge:
        # Handle the specific error for large files
        flash(f"Files are too large. Maximum upload size is {max_upload_size} MB.", 'alert-danger')
        return False
    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}", 'alert-danger')
        return False


def create_csv(file_path):
    # TODO Read data from the database
    data = {
        'Company': ['LMT', 'CircleK', 'KKas'],
        'Reg. Number': ['AF123', 'AF234', 'AF345'],
        'Product': ['Mobilais internets', 'Benzīns', 'Cepumi']
    }
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)


def file_download(file_type):
    report_folder = current_app.config['REPORT_FOLDER']

    # get current date and time -> date,month,year  hour,minute,second
    current_datetime = datetime.now().strftime("%d%m%Y_%H%M%S")

    # Get current users id
    user_id = session.get('user_id')
    # Find user in database
    user = User.query.get(user_id) if user_id else None
    # Get username for current user
    username = user.username if user and user.username else ""
    # Get group and replace spaces in group name with an underscore
    group = user.group.replace(" ", "_") if user and user.group else ""

    filename = f'report-{username}-{group}-{current_datetime}.csv'
    file_path = os.path.join(report_folder, filename)

    # TODO Delete the csv file when no longer needed
    # Create a summary of the invoices in csv format
    if file_type == 'summary':
        try:
            # Create csv file
            create_csv(file_path)
            # Send file to user
            return send_from_directory(report_folder, filename, as_attachment=True)
        except Exception as e:
            flash(f'Download failed: {str(e)}', 'alert-danger')
            return False

    # TODO Create a summary of the emissions in pdf or excel format
    elif file_type == 'report':
        # try:
        #     filename = 'report.txt'  # Name of the specific file to be downloaded
        #     file_path = os.path.join(report_folder, filename)
        #     with open(file_path, 'w', encoding='utf-8') as file:
        #         file.write('Paldies, ka lejupielādēji vīrusu. Datu šifrēšana ir progresā.\n')
        #     return send_from_directory(report_folder, filename, as_attachment=True)
        # except Exception as e:
        #     flash(f'Download failed: {str(e)}', 'alert-danger')
        return False
    else:
        flash(f'Download failed: Incorrect redirect', 'alert-danger')
        return False


def insert_file_in_db(filename, file_data):
    # TODO check if the correct user
    user_id = session['user_id']
    new_file = File(user_id=user_id, title=filename, file_data=file_data)
    db.session.add(new_file)
    db.session.commit()
    # session['file_id'] = new_file.id
    return new_file.id

