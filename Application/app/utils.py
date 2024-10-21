from flask import flash, request, current_app, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import os

def file_upload():
    allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
    max_upload_size = current_app.config['MAX_UPLOAD_SIZE']
    upload_folder = current_app.config['UPLOAD_FOLDER']
    try:
        files = request.files.getlist('file')
        # If no file is selected
        if not files or files[0].filename == '':
            flash('No file selected', 'alert-danger')
            return False
        # If incorrect file extension
        for file in files:
            if file.filename.rsplit('.',1)[1].lower() not in allowed_extensions:
                flash(f'Invalid file format for {file.filename}', 'alert-danger')
                continue  # Skip the invalid file
            # If file is allowed
            # Secure the filename and save it to the upload folder
            filename = secure_filename(file.filename)
            file.save(os.path.join(upload_folder, filename))
            flash(f"File uploaded successfully: {filename}", 'alert-success')
        return True

    except RequestEntityTooLarge:
        # Handle the specific error for large files
        flash(f"File is too large. Maximum size allowed is {max_upload_size} MB.", 'alert-danger')
        return False
    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}", 'alert-danger')
        return False

def file_download():
    report_folder = current_app.config['REPORT_FOLDER']
    try:
        filename = 'report.txt'  # Name of the specific file to be downloaded
        file_path = os.path.join(report_folder, filename)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write('Paldies, ka lejupielādēji vīrusu. Datu šifrēšana ir progresā.\n')
        return send_from_directory(report_folder, filename, as_attachment=True)
    except Exception as e:
        flash(f'Download failed: {str(e)}', 'alert-danger')
        return False