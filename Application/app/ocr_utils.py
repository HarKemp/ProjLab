import fitz  # PyMuPDF
import pytesseract # For unix systems make sure tesseract is installed sudo apt get install tesseract
from pdf2image import convert_from_bytes
import cv2
import numpy as np
import google.generativeai as genai
import json
from datetime import datetime
import typing_extensions as typing
from app.database.models import Service, Invoice, Emission, get_emission_value, EmissionValue
from app.__init__ import db
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)
class Order(typing.TypedDict):
    OrderNumber: str
    Customer: str
    CustomerAdress: str
    Supplier: str
    Goods: list[str]
    OrderedAmount: list[str]
    OrderDate: str
    Cost: str
    SeparateCosts: list[str]
    SupplierAdress: str
    SupplierRegNumber: str
    CustomerRegNumber: str
    Categories: list[str]

model = genai.GenerativeModel(model_name="gemini-1.5-flash")

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
def image_smoothen(img):
    # Step 1: Convert the image to grayscale if not already
    if len(img.shape) == 3:  # If the image has 3 channels (RGB), convert to grayscale
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    smoothed = cv2.bilateralFilter(img, d=5, sigmaColor=75, sigmaSpace=75)

    # Step 3: Apply non-local means denoising for better noise reduction
    denoised = cv2.fastNlMeansDenoising(smoothed, h=30)

    # Step 4: Apply adaptive thresholding to binarize the image
    th = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # cv2.imwrite('img.png', th)

    return th

# Function to extract text and blocks from PDF
def extract_text_from_pdf(pdf_file,lang='lav'):
    pdf_bytes = pdf_file.read() if hasattr(pdf_file, 'read') else pdf_file
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    ocr_results = []  # To store OCR results for each page
    images = convert_from_bytes(pdf_bytes,dpi=300)

    for page_num, image in enumerate(images, start=1):
        imagenp =np.asarray(image)
        image_smh = image_smoothen(np.asarray(imagenp))
        ocr_data = pytesseract.image_to_data(image_smh,lang=lang,config='--psm 6',output_type=pytesseract.Output.DATAFRAME)
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

def combine_text_by_word_clustering(ocr_results, proximity_threshold=10):
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


def create_prompt():

    categories = EmissionValue.query.all()
    category_list = "; ".join(f"{category.name}" for category in categories)

    prompt = f"""
    Extract the following information from the invoice text provided, using only the information present in the text. 
    If a piece of information cannot be found, indicate it with 'N/A'.
    Info required from invoice
    1. Buyer (Pircējs): The individual or organization making the purchase and paying the invoice.
    2. Service Provider (Pakalpojuma sniedzējs): The individual or organization providing the service or goods - if there are multiple headers, evaluate and include only the most logical ones for a given price or quantity.   
    3. Supplier Registration Number (SupplierRegNumber): The registration number of the service provider.
    4. Items/Services (Pakalpojums/Prece): A list of all items or services purchased. If multiple items are ordered, list each one and its price.
    If the service is electricity, specify the Item Quantity (Amount) in kilowatt-hours (kWh) only for the main electricity consumption statistic itself (Elektroenerģija or similar).
    5. Item Quantity (Amount): The quantity of each item ordered. If the quantity cannot be determined, assume it is 1.
    6. Price per Item with VAT (SeparateCosts): The price of each item or service, including VAT. Include the currency symbol or denominator (like EUR) if it's in the text.
    7. Total Cost with VAT (Cost): The total amount due on the invoice, including VAT. Include the currency symbol if it's in the text.
    8. Invoice Number (Rēķina numurs): The invoice's unique identifying number.  
    9. Invoice Date (Rēķina datums): The date the invoice was issued as %dd.%mm.%yyyy if found.
    10. Currency (Valūta): The currency in which the invoice is issued.
    11. Categories: The category of the service or item. Guess a category for each service in the invoice. If multiple items are ordered, provide a category for each one. If the category is not clear, use the most likely one.
    Categories available for services: {category_list}
    Input the extracted information into the provided class structure.
    Output the extracted information in the provided JSON schema.
    Ensure the JSON output is well-formed and properly escaped. Do not put any escape characters (like quotes or newlines) in the json. Do not put more than one backslash n or backslash t in a row for any of the values in the json.
    """

    return prompt

def get_ai_result(ocr_results):
    # Combine text by clustering nearby words
    combined_blocks = combine_text_by_word_clustering(ocr_results, proximity_threshold=20)

    total_text = ""
    for block in combined_blocks:
        total_text += block['combined_text']

    prompt = create_prompt()
    print(prompt)

    response = model.generate_content(
        [prompt, total_text],
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=list[Order],
            temperature=0.4,
            max_output_tokens=500
        )
    )
    try:
        print("AI response:", response.text)
        json_data = json.loads(response.text)
    except Exception as e:
        print("Error parsing JSON response: ",e)
        return None, 1

    return json_data[0], 0

def send_invoice(response, file_id):
    print(response)
    try:
        goods = response['Goods']
        emission_categories = response.get('Categories', [])
    except Exception as e:
        print("Error parsing JSON response: ",e)
        return False
    services = []

    for j in range(len(goods)):
        try:
            name = goods[j]
            emission_category = emission_categories[j] if j < len(emission_categories) else None
            price = response['SeparateCosts'][j]
            amount = response['OrderedAmount'][j]
            service = Service(name=name, price=price, amount=amount)
            db.session.add(service)
            db.session.commit()

            emission_coefficient = get_emission_value(emission_category)
            print("emission coefficient = " + str(emission_coefficient))
            emission = Emission(service_id=service.id, value=emission_coefficient)
            db.session.add(emission)
            db.session.commit()

            print(f"Service {service.name} (category: {emission_category}) has emission {emission_coefficient} "
                  f""f"amount={service.amount}, totaling {service.total_emissions}")
            services.append(service)
        except Exception as e:
            # Print any other unexpected error
            print("An error occurred:", e)
    try:
        invoice = Invoice.query.filter_by(file_id=file_id).first()
        if invoice:
            invoice.issuer = response.get('Supplier', 'N/A')
            invoice.issuer_registration_number = response.get('SupplierRegNumber', 'N/A')
            invoice.issuer_address = response.get('SupplierAdress', 'N/A')
            invoice.receiver = response.get('Customer', 'N/A')
            invoice.receiver_registration_number = response.get('CustomerRegNumber', 'N/A')
            invoice.receiver_address = response.get('CustomerAdress', 'N/A')
            issue_date_str = response.get('OrderDate', 'N/A')
            try:
                invoice.issue_date = datetime.strptime(issue_date_str, "%d.%m.%Y")
            except Exception as e:
                print("Error parsing date:", e)
                # Set the issue date to the current date if parsing fails
                invoice.issue_date = datetime.now()
            invoice.issue_number = response.get('OrderNumber', 'N/A')
            invoice.sum_total = response.get('Cost', 'N/A')
            invoice.services = services
        print("invoice from " + str(invoice.issuer) + " shows that carbon footprint for services is totaling " + str(invoice.total_emissions))
        db.session.commit()
        print("invoice:")
        print(invoice)
        return True

    except Exception as e:
            # Print any other unexpected error
            print("An error occurred:", e)
            return False

def doc2data(file):
    ocr_results = extract_text_from_pdf(file.file_data)
    ai_result, err = get_ai_result(ocr_results)
    if err == 1:
        return False
    # Save invoice into DB
    return send_invoice(ai_result, file.id)