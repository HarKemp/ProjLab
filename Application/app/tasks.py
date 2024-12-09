from . import create_app
import time
from .db.models import File, db
# from celery import shared_task
from .celery_utils import celery

app = create_app()
# @shared_task
@celery.task
def ocr_task(file_id):
    with app.app_context():
        file = File.query.get(file_id)
        if file is None:
            return "File not found."

        # Set status to "Processing"
        file.ocr_status = "Processing"
        db.session.commit()

        # Mock OCR processing time
        time.sleep(10)  # Simulates a 5-second processing delay

        # Simulate OCR text content
        file.text_content = "This is a test OCR result."

        # Set status to "Complete"
        file.ocr_status = "Complete"
        db.session.commit()
        # OCR processing logic
        # Example: read file, perform OCR, and save result
        # result = perform_ocr(file_path)  # Replace with your actual OCR function
        return f"OCR complete for file ID: {file_id}"

def perform_ocr(file_path):
    # Implement your OCR processing here
    return f"OCR processing complete for {file_path}"