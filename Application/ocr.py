import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import io

def ocr_pdf_to_text(pdf_path, tess_path=None):
    """
    Extracts text from a PDF using both direct text extraction and OCR (for scanned PDFs).
    
    Args:
    - pdf_path (str): Path to the PDF file.
    - tess_path (str): Path to Tesseract OCR executable (if it's not in the system's PATH).
    
    Returns:
    - text (str): The extracted text from the PDF.
    """
    if tess_path:
        pytesseract.pytesseract.tesseract_cmd = tess_path
    
    text = ""
    
    # Open the PDF with PyMuPDF
    pdf_document = fitz.open(pdf_path)
    
    # Loop through each page
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        
        # Extract text directly (useful for PDFs that are not scanned)
        extracted_text = page.get_text("text")
        
        if extracted_text.strip():
            # If text is found, append it
            text += extracted_text
        else:
            # Perform OCR if no text is found
            print(f"Performing OCR on page {page_num + 1}...")
            page_images = convert_from_path(pdf_path, first_page=page_num + 1, last_page=page_num + 1, dpi=300)
            
            for img in page_images:
                img_byte_array = io.BytesIO()
                img.save(img_byte_array, format='PNG')  
                img = Image.open(io.BytesIO(img_byte_array.getvalue()))  
                ocr_text = pytesseract.image_to_string(img)
                text += ocr_text
    
    pdf_document.close()
    
    return text

# Example usage
pdf_path = "example.pdf"
text_output = ocr_pdf_to_text('ocr_test_files/LMT.pdf')
print(text_output)
