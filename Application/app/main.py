from flask import Blueprint, render_template, url_for, request, redirect, jsonify
from flask_login import login_required, current_user
from app.database.models import File, Invoice
from decimal import Decimal
from sqlalchemy import desc

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
            return redirect(url_for('main.homepage'))
        else:
            return redirect(request.url)
    
    # Get all services for current user's invoices
    invoices = Invoice.query.filter_by(user_id=current_user.id).all()
    
    # Store service totals in a dictionary
    service_totals = {}
    
    # Calculate totals for each service type across all invoices
    for invoice in invoices:
        for service in invoice.services:
            service_name = service.name
            if service_name not in service_totals:
                service_totals[service_name] = 0
            service_totals[service_name] += service.total_emissions
    
    # Convert to lists for the chart
    labels = list(service_totals.keys())
    emissions_data = [float(value) for value in service_totals.values()]
    
    return render_template("homepage.html", 
                         pie_labels=labels,
                         pie_data=emissions_data)

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

@main.route('/my-invoices', methods=['GET'])
@login_required
def my_invoices():
    # Obtain all invoices for current user
    invoices = Invoice.query.filter_by(user_id=current_user.id).all()
    return render_template("invoices.html", invoices=invoices)

@main.route('/my-invoices/invoice/<int:invoice_id>', methods=['GET'])
@login_required
def invoice(invoice_id):
    if invoice_id is None or not isinstance(invoice_id, int) or invoice_id < 1:
        print("illegal invoice ID")
        return redirect(url_for('main.homepage'))
    else:
        user_id = current_user.id
        invoice = Invoice.query.filter_by(id=invoice_id, user_id=user_id).first()
        return render_template('invoice.html', invoice=invoice)

# Runs when requested by the client side (usually every 10 seconds when the specific webpage is open)
@main.route('/invoice-status', methods=['GET'])
@login_required
def invoice_status():
    # Obtain all invoices for current user
    invoices = Invoice.query.filter_by(user_id=current_user.id).all()
    data = []
    # Send data about invoices in json format
    for inv in invoices:
        # Display total_emissions with a decimal point - consistent with default display
        total_emissions = str(round(Decimal(str(inv.total_emissions)), 1))
        
        data.append({
            'id': inv.id,
            'ocr_status': inv.file.ocr_status if inv.file else 'Error',
            'issuer': inv.issuer,
            'issuer_address': inv.issuer_address,
            'receiver': inv.receiver,
            'receiver_address': inv.receiver_address,
            'issue_number': inv.issue_number,
            'issue_date': inv.issue_date.strftime('%Y-%m-%d') if inv.issue_date else 'N/A',
            'sum_total': inv.sum_total,
            'services_count': len(inv.services),
            'total_emissions': total_emissions,
            'issuer_registration_number': inv.issuer_registration_number,
            'receiver_registration_number': inv.receiver_registration_number,
        })
    return jsonify(data)

@main.route("/chart", methods=['GET', 'POST'])
@login_required
def chart():
    # Get all invoices and their services for current user
    invoices = Invoice.query.filter_by(user_id=current_user.id).all()
    
    # Create a dictionary to store service totals
    service_totals = {}
    
    # Calculate totals for each service type across all invoices
    for invoice in invoices:
        for service in invoice.services:
            service_name = service.name
            if service_name not in service_totals:
                service_totals[service_name] = {
                    'total_emissions': 0,
                    'emission_value': service.emission.value if service.emission else 0
                }
            
            service_totals[service_name]['total_emissions'] += service.total_emissions
    
    # Get top 5 services
    top_services = sorted(
        service_totals.items(), 
        key=lambda x: x[1]['total_emissions'], 
        reverse=True
    )[:5]
    
    # Prepare data for the chart
    labels = [service[0] for service in top_services]
    emissions_data = [float(service[1]['total_emissions']) for service in top_services]
    
    return render_template("chart.html", 
                         invoices=invoices, 
                         labels=labels,
                         emissions_data=emissions_data)

def validate_id(invoice_id):
    try:
        # Validate if invoice_id can be converted to an integer
        invoice_id = int(invoice_id)
        return invoice_id
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid ID format. ID must be an integer.'}), 400

@main.route('/my-invoices/invoice/<int:invoice_id>/delete', methods=['DELETE'])
@login_required
def delete_fruit(invoice_id):
    invoice_id = validate_id(invoice_id)

    if invoice_id:
        invoice_to_delete = Invoice.query.get(int(invoice_id))
        success = invoice_to_delete.delete()
        if success:
            return jsonify({'success': True, 'message': 'Row deleted successfully'}), 200
        else:
            return jsonify({'success': False, 'message': 'Row not found'}), 404

    return jsonify({'success': False, 'message': 'No ID provided'}), 400

@main.route('/my-invoices/invoice/<int:invoice_id>/update', methods=['PUT'])
@login_required
def update_invoice(invoice_id):
    data = request.get_json()
    print(data)
    invoice_id = validate_id(invoice_id)
    if invoice_id:
        invoice_to_update = Invoice.query.get(invoice_id)

        success = invoice_to_update.update(data)
        if success:
            return jsonify({'success': True, 'message': 'Invoice updated successfully'}), 200
        else:
            return jsonify({'success': False, 'message': 'Error updating invoice'}), 500

    return jsonify({'success': False, 'message': 'Invoice not found'}), 404