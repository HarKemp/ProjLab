from app.celery_init import celery, celery_app
from app.database.models import File
from app.__init__ import db
from app.ocr_utils import doc2data
import time

@celery.task
def ocr_task(file_id):
    with celery_app.app_context():
        file = File.query.get(file_id)
        if file is None:
            return "File not found."

        file.ocr_status = "Processing"
        db.session.commit()

        # Perform OCR
        doc2data(file)

        file.ocr_status = "Complete"
        db.session.commit()

        return f"OCR complete for file ID: {file_id}"