from app.celery_init import celery, celery_app
import time
from app.db.models import File
from app.extensions import db
###### app.__init__ import db ????

@celery.task
def ocr_task(file_id):
    with celery_app.app_context():
        file = File.query.get(file_id)
        if file is None:
            return "File not found."

        file.ocr_status = "Processing"
        db.session.commit()

        time.sleep(10)  # Simulates a 5-second processing delay

        file.ocr_status = "Complete"
        db.session.commit()

        # result = perform_ocr(file_path)  # Replace with your actual OCR function
        return f"OCR complete for file ID: {file_id}"