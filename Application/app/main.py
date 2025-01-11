from flask import Blueprint, render_template, url_for, request, redirect, jsonify
from flask_login import login_required, current_user
from app.database.models import File, Invoice, Service, Emission, invoices_services
from decimal import Decimal
from sqlalchemy import desc, func
from datetime import datetime

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
            if service.total_emissions > 0:  # Check emissions before adding
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
    
# Route for emissions charts - returns data for top 5 services and historical emissions when called by the user
@main.route("/api/emissions")
@login_required
def get_filtered_emissions():
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    try:
        # Base query for filtered data - invoices between start and end date
        base_query = Invoice.query.filter(
            Invoice.user_id == current_user.id,
            Invoice.issue_date >= datetime.strptime(start_date, '%Y-%m-%d'),
            Invoice.issue_date <= datetime.strptime(end_date, '%Y-%m-%d')
        )

        if base_query.count() == 0:
            return jsonify({
                'labels': [],
                'emissions_data': [],
                'timeline_labels': [],
                'timeline_emissions': [],
                'message': 'No data found for the selected date range'
            })

        # Get monthly data
        monthly_data = (base_query
            .with_entities(
                func.extract('year', Invoice.issue_date).label('year'),
                func.extract('month', Invoice.issue_date).label('month'),
                func.sum(Service.amount * Emission.value).label('monthly_emissions')
            )
            .join(Invoice.services)
            .join(Service.emission)
            .group_by('year', 'month')
            .order_by('year', 'month')
            .all()
        )

        # Format monthly data for timeline chart
        timeline_labels = []
        timeline_emissions = []
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        # Append labels to list (used for x-axis)
        for year, month, emissions in monthly_data:
            timeline_labels.append(f"{months[int(month)-1]} {int(year)}")
            timeline_emissions.append(float(emissions))

        # Get top 5 services
        top_services = (Service.query
            .with_entities(
                Service.name,
                func.sum(Service.amount * Emission.value).label('total_emissions')
            )
            .join(Service.emission)
            .join(Service.invoice)
            .filter(
                Invoice.id.in_(base_query.with_entities(Invoice.id))
            )
            .group_by(Service.name)
            .order_by(desc('total_emissions'))
            .limit(5)
            .all()
        )

        # Return data in JSON format
        return jsonify({
            'labels': [service[0] for service in top_services],
            'emissions_data': [float(service[1]) for service in top_services], # Contains total emissions for top 5 services
            'timeline_labels': timeline_labels, # Contains labels for timeline chart - x-axis data
            'timeline_emissions': timeline_emissions # Contains emissions data for timeline chart - y-axis data
        })

    except Exception as e: # On exception, return 400 status code + error message
        return jsonify({
            'labels': [],
            'emissions_data': [],
            'timeline_labels': [],
            'timeline_emissions': [],
            'message': str(e)
        }), 400 

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
        return redirect(url_for('main.my_invoices'))
    else:
        user_id = current_user.id
        invoice = Invoice.query.filter_by(id=invoice_id, user_id=user_id).first()
        if invoice is None:
            return redirect(url_for('main.my_invoices'))

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
    # Get top 5 services with highest emissions
    top_services = (Service.query
        .with_entities(
            Service.name,
            func.sum(Service.amount * Emission.value).label('total_emissions')
        )
        .join(Service.emission)
        .join(Service.invoice)
        .filter(Invoice.user_id == current_user.id)
        .group_by(Service.name)
        .order_by(desc('total_emissions'))
        .limit(5)
        .all()
    )

    # Convert data to lists for the chart
    labels = [service[0] for service in top_services]
    emissions_data = [float(service[1]) for service in top_services]

    # Get historical data for historical emission chart - default is yearly
    historical_data = (Invoice.query
        .with_entities(
            func.extract('year', Invoice.issue_date).label('year'),
            func.sum(Service.amount * Emission.value).label('yearly_emissions')
        )
        .join(Invoice.services)
        .join(Service.emission)
        .filter(Invoice.user_id == current_user.id)
        .group_by('year')
        .order_by('year')
        .all()
    )

    years = [int(data[0]) for data in historical_data]
    yearly_emissions = [float(data[1]) for data in historical_data]

    return render_template(
        "chart.html",
        labels=labels, # Contains service names for top 5 services
        emissions_data=emissions_data, # Contains total emissions for top 5 services
        years=years, # Contains years for historical emissions
        yearly_emissions=yearly_emissions # Contains total emissions for each year
    )

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