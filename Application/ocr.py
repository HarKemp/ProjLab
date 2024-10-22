import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import io
import os
# import google.generativeai as genai
# #pip install -U google-generativeai 
# #apt-get install poppler-utils
# # genai.configure(api_key='')
# # model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# def ocr_pdf_to_text(pdf_path, tess_path=None):
#     """
#     Extracts text from a PDF using both direct text extraction and OCR (for scanned PDFs).
    
#     Args:
#     - pdf_path (str): Path to the PDF file.
#     - tess_path (str): Path to Tesseract OCR executable (if it's not in the system's PATH).
    
#     Returns:
#     - text (str): The extracted text from the PDF.
#     """
#     if tess_path:
#         pytesseract.pytesseract.tesseract_cmd = tess_path
    
#     text = ""
    
#     # Open the PDF with PyMuPDF
#     pdf_document = fitz.open(pdf_path)
    
#     # Loop through each page
#     for page_num in range(len(pdf_document)):
#         page = pdf_document.load_page(page_num)
        
#         # Extract text directly (useful for PDFs that are not scanned)
#         extracted_text = page.get_text("text")
        
#         if extracted_text.strip():
#             # If text is found, append it
#             text += extracted_text
#             #print(extracted_text)
#         else:
#             # Perform OCR if no text is found
#             print(f"Performing OCR on page {page_num + 1}...")
#             page_images = convert_from_path(pdf_path, first_page=page_num + 1, last_page=page_num + 1, dpi=1200)
            
#             for img in page_images:
#                 img_byte_array = io.BytesIO()
#                 img.save(img_byte_array, format='PNG')  
#                 img = Image.open(io.BytesIO(img_byte_array.getvalue()))  
#                 ocr_text = pytesseract.image_to_string(img, lang='lva')
#                 text += ocr_text
                
#     pdf_document.close()
    
#     return text

# # Example usage
# pdf_path = "example.pdf"
# text_output = ocr_pdf_to_text('ocr_test_files/LMT.pdf')

# print(text_output)

# # prompt = "Iegūsti informāciju no rēķina teksta: Kas ir pasūtītājs/kas apmaksā/kas ir pircējs?- Kas sniedz pakalpojumu?- Par ko tiek maksāts un cik tas maksā ar PVN? - kāds ir rēķina numurs? -kāds ir rēķina datums?"

# # response = model.generate_content([prompt, text_output])

# # print(response.text)
# Example usage
# Function to extract text and blocks from PDF
# Helper function to check if two rectangles overlap or are close
def are_rectangles_close(rect1, rect2, threshold=100):
    x0_1, y0_1, x1_1, y1_1 = rect1
    x0_2, y0_2, x1_2, y1_2 = rect2

    # Check if the rectangles are close by threshold or overlap
    if (x1_1 + threshold >= x0_2 >= x0_1 - threshold or
        x1_2 + threshold >= x0_1 >= x0_2 - threshold) and \
       (y1_1 + threshold >= y0_2 >= y0_1 - threshold or
        y1_2 + threshold >= y0_1 >= y0_2 - threshold):
        return True
    return False

# Function to merge rectangles into one larger rectangle
def merge_rectangles(rect1, rect2):
    x0_1, y0_1, x1_1, y1_1 = rect1
    x0_2, y0_2, x1_2, y1_2 = rect2
    return (min(x0_1, x0_2), min(y0_1, y0_2), max(x1_1, x1_2), max(y1_1, y1_2))

# Function to extract text and blocks from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    ocr_results = []  # To store OCR results for each page
    images = convert_from_path(pdf_path)

    for page_num, image in enumerate(images, start=1):
        ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DATAFRAME)
        ocr_data = ocr_data.dropna(subset=['text']).reset_index(drop=True)
        pdf_page = doc.load_page(page_num - 1)
        text_blocks = pdf_page.get_text("blocks")
        pdf_width, pdf_height = pdf_page.rect.width, pdf_page.rect.height
        image_width, image_height = image.size
        x_scale = pdf_width / image_width
        y_scale = pdf_height / image_height
        page_results = {
            'page_number': page_num,
            'ocr_data': ocr_data,
            'pdf_blocks': text_blocks,
            'x_scale': x_scale,
            'y_scale': y_scale,
        }
        ocr_results.append(page_results)

    return ocr_results

def combine_text_by_word_clustering(ocr_results, proximity_threshold=30):
    combined_blocks = []

    for page_result in ocr_results:
        ocr_data = page_result['ocr_data']
        x_scale = page_result['x_scale']
        y_scale = page_result['y_scale']
        page_number = page_result['page_number']

        # Create a list to store clusters of words
        word_clusters = []

        print(f"\nProcessing Page {page_number}:")

        # Loop through each word and cluster nearby words
        for index, row in ocr_data.iterrows():
            word_left = row['left'] * x_scale
            word_top = row['top'] * y_scale
            word_right = (row['left'] + row['width']) * x_scale
            word_bottom = (row['top'] + row['height']) * y_scale
            
            current_word_rect = (word_left, word_top, word_right, word_bottom)
            added_to_cluster = False
            
            # Check if this word can be added to an existing cluster
            for cluster in word_clusters:
                if are_rectangles_close(cluster['bounding_box'], current_word_rect, threshold=proximity_threshold):
                    cluster['words'].append(row['text'])
                    cluster['bounding_box'] = merge_rectangles(cluster['bounding_box'], current_word_rect)
                    added_to_cluster = True
                    break
            
            # If the word was not added to any cluster, create a new cluster
            if not added_to_cluster:
                word_clusters.append({
                    'words': [row['text']],
                    'bounding_box': current_word_rect
                })

        # Combine the words in each cluster into a single string
        for cluster in word_clusters:
            combined_text = ' '.join(cluster['words'])
            combined_blocks.append({
                'page_number': page_number,
                'block_position': cluster['bounding_box'],
                'combined_text': combined_text
            })

    return combined_blocks

# Example usage
pdf_path = 'ocr_test_files/LMT.pdf'

ocr_results = extract_text_from_pdf(pdf_path)

# Combine text by clustering nearby words
combined_blocks = combine_text_by_word_clustering(ocr_results, proximity_threshold=20)

# Output: combined_blocks will contain combined text for clustered words
for block in combined_blocks:
    print(f"{block['combined_text']}")
    print()



# Example usage
