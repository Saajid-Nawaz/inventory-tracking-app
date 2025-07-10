import os
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from PIL import Image
import logging
from datetime import datetime

from app import app, db
from models import User, MaterialRecord, IssuanceLog, IssuanceRequest, BatchIssuance, BatchIssuanceItem
from ocr_processor import extract_materials_from_image
from excel_manager import ExcelManager
import random
import string

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize default users if they don't exist
def create_default_users():
    if not User.query.filter_by(username='engineer').first():
        engineer = User(username='engineer', role='site_engineer')
        engineer.set_password('engineer123')
        db.session.add(engineer)
        
    if not User.query.filter_by(username='storesperson').first():
        storesperson = User(username='storesperson', role='storesperson')
        storesperson.set_password('store123')
        db.session.add(storesperson)
        
    db.session.commit()

# Create default users when the app starts
with app.app_context():
    create_default_users()

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'site_engineer':
            return redirect(url_for('site_engineer'))
        elif current_user.role == 'storesperson':
            return redirect(url_for('storesperson'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            if user.role == 'site_engineer':
                return redirect(url_for('site_engineer'))
            elif user.role == 'storesperson':
                return redirect(url_for('storesperson'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/site_engineer')
@login_required
def site_engineer():
    if current_user.role != 'site_engineer':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get recent material records
    recent_records = MaterialRecord.query.filter_by(recorded_by=current_user.username).order_by(MaterialRecord.recorded_at.desc()).limit(10).all()
    
    return render_template('site_engineer.html', recent_records=recent_records)

@app.route('/upload_photo', methods=['POST'])
@login_required
def upload_photo():
    if current_user.role != 'site_engineer':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if 'photo' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('site_engineer'))
    
    file = request.files['photo']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('site_engineer'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to filename to avoid conflicts
        import time
        filename = f"{int(time.time())}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process image with OCR
        try:
            materials = extract_materials_from_image(filepath)
            session['temp_materials'] = materials
            session['temp_image'] = filename
            
            if materials:
                return redirect(url_for('preview_materials'))
            else:
                flash('No materials detected in the image. Please try again with a clearer image.', 'warning')
                return redirect(url_for('site_engineer'))
                
        except Exception as e:
            logging.error(f"Error processing image: {str(e)}")
            flash('Error processing image. Please try again.', 'error')
            return redirect(url_for('site_engineer'))
    
    flash('Invalid file type. Please upload an image file.', 'error')
    return redirect(url_for('site_engineer'))

@app.route('/manual_entry', methods=['POST'])
@login_required
def manual_entry():
    if current_user.role != 'site_engineer':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Handle optional photo upload
    image_filename = None
    if 'photo' in request.files:
        file = request.files['photo']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to filename to avoid conflicts
            import time
            filename = f"{int(time.time())}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            image_filename = filename
    
    # Extract materials from form data
    materials = []
    i = 0
    while f'material_name_{i}' in request.form:
        material_name = request.form.get(f'material_name_{i}')
        quantity = request.form.get(f'quantity_{i}')
        unit = request.form.get(f'unit_{i}')
        
        if material_name and quantity and unit:
            try:
                quantity = float(quantity)
                if quantity > 0:
                    materials.append({
                        'name': material_name.strip(),
                        'quantity': quantity,
                        'unit': unit
                    })
            except ValueError:
                flash(f'Invalid quantity for {material_name}', 'error')
                return redirect(url_for('site_engineer'))
        i += 1
    
    if not materials:
        flash('No valid materials entered', 'warning')
        return redirect(url_for('site_engineer'))
    
    # Save materials to database
    try:
        for material in materials:
            record = MaterialRecord(
                material_name=material['name'],
                quantity=material['quantity'],
                unit=material['unit'],
                image_filename=image_filename,
                recorded_by=current_user.username,
                status='confirmed'
            )
            db.session.add(record)
        
        db.session.commit()
        
        # Update Excel file
        excel_manager = ExcelManager()
        excel_manager.update_stock(materials)
        
        flash(f'Successfully recorded {len(materials)} materials', 'success')
        logging.info(f"Manual entry: {current_user.username} recorded {len(materials)} materials")
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error saving manual materials: {str(e)}")
        flash('Error saving materials. Please try again.', 'error')
    
    return redirect(url_for('site_engineer'))

@app.route('/preview_materials')
@login_required
def preview_materials():
    if current_user.role != 'site_engineer':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    materials = session.get('temp_materials', [])
    image_filename = session.get('temp_image', '')
    
    if not materials:
        flash('No materials to preview', 'warning')
        return redirect(url_for('site_engineer'))
    
    return render_template('preview_materials.html', materials=materials, image_filename=image_filename)

@app.route('/confirm_materials', methods=['POST'])
@login_required
def confirm_materials():
    if current_user.role != 'site_engineer':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    materials = session.get('temp_materials', [])
    image_filename = session.get('temp_image', '')
    
    if not materials:
        flash('No materials to confirm', 'warning')
        return redirect(url_for('site_engineer'))
    
    # Get form data
    confirmed_materials = []
    for i, material in enumerate(materials):
        material_name = request.form.get(f'material_{i}')
        quantity = request.form.get(f'quantity_{i}')
        unit = request.form.get(f'unit_{i}')
        
        if material_name and quantity and unit:
            try:
                quantity = float(quantity)
                confirmed_materials.append({
                    'name': material_name,
                    'quantity': quantity,
                    'unit': unit
                })
            except ValueError:
                flash(f'Invalid quantity for {material_name}', 'error')
                return redirect(url_for('preview_materials'))
    
    if not confirmed_materials:
        flash('No valid materials confirmed', 'warning')
        return redirect(url_for('preview_materials'))
    
    # Save to database
    for material in confirmed_materials:
        record = MaterialRecord(
            material_name=material['name'],
            quantity=material['quantity'],
            unit=material['unit'],
            image_filename=image_filename,
            recorded_by=current_user.username,
            status='confirmed'
        )
        db.session.add(record)
    
    db.session.commit()
    
    # Update Excel file
    try:
        excel_manager = ExcelManager()
        excel_manager.update_stock(confirmed_materials)
        flash(f'Successfully recorded {len(confirmed_materials)} materials', 'success')
    except Exception as e:
        logging.error(f"Error updating Excel file: {str(e)}")
        flash('Materials recorded but Excel update failed', 'warning')
    
    # Clear session data
    session.pop('temp_materials', None)
    session.pop('temp_image', None)
    
    return redirect(url_for('site_engineer'))

@app.route('/storesperson')
@login_required
def storesperson():
    if current_user.role != 'storesperson':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get current stock from Excel
    try:
        excel_manager = ExcelManager()
        current_stock = excel_manager.get_current_stock()
        recent_issuances = IssuanceLog.query.order_by(IssuanceLog.issued_at.desc()).limit(10).all()
        pending_requests = IssuanceRequest.query.filter_by(
            requested_by=current_user.username
        ).order_by(IssuanceRequest.requested_at.desc()).limit(10).all()
        
        return render_template('storesperson.html', 
                             current_stock=current_stock, 
                             recent_issuances=recent_issuances,
                             pending_requests=pending_requests)
    except Exception as e:
        logging.error(f"Error reading Excel file: {str(e)}")
        flash('Error reading stock data', 'error')
        return render_template('storesperson.html', current_stock=[], recent_issuances=[], pending_requests=[])



@app.route('/get_stock_data')
@login_required
def get_stock_data():
    if current_user.role != 'storesperson':
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        excel_manager = ExcelManager()
        current_stock = excel_manager.get_current_stock()
        return jsonify({'stock': current_stock})
    except Exception as e:
        logging.error(f"Error getting stock data: {str(e)}")
        return jsonify({'error': 'Error reading stock data'}), 500

@app.route('/materials_dashboard')
@login_required
def materials_dashboard():
    # Get current stock from Excel
    excel_manager = ExcelManager()
    current_stock = excel_manager.get_current_stock()
    
    # Get all material records
    material_records = MaterialRecord.query.order_by(MaterialRecord.recorded_at.desc()).limit(50).all()
    
    return render_template('materials_dashboard.html', 
                         current_stock=current_stock,
                         material_records=material_records)

@app.route('/request_issuance', methods=['POST'])
@login_required
def request_issuance():
    if current_user.role != 'storesperson':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    material_name = request.form.get('material_name')
    quantity_requested = request.form.get('quantity_requested')
    unit = request.form.get('unit')
    purpose = request.form.get('purpose')
    
    if not all([material_name, quantity_requested, unit]):
        flash('All fields are required', 'error')
        return redirect(url_for('materials_dashboard'))
    
    try:
        quantity_requested = float(quantity_requested)
        if quantity_requested <= 0:
            flash('Quantity must be greater than 0', 'error')
            return redirect(url_for('materials_dashboard'))
        
        # Create issuance request
        issuance_request = IssuanceRequest(
            material_name=material_name,
            quantity_requested=quantity_requested,
            unit=unit,
            requested_by=current_user.username,
            purpose=purpose
        )
        
        db.session.add(issuance_request)
        db.session.commit()
        
        flash('Issuance request submitted for approval', 'success')
        logging.info(f"Issuance request: {current_user.username} requested {quantity_requested} {unit} of {material_name}")
        
    except ValueError:
        flash('Invalid quantity value', 'error')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating issuance request: {str(e)}")
        flash('Error submitting request. Please try again.', 'error')
    
    return redirect(url_for('materials_dashboard'))

@app.route('/approval_dashboard')
@login_required
def approval_dashboard():
    if current_user.role != 'site_engineer':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get pending individual requests
    pending_requests = IssuanceRequest.query.filter_by(status='pending').order_by(IssuanceRequest.requested_at.desc()).all()
    
    # Get pending batch requests
    pending_batch_requests = BatchIssuance.query.filter_by(status='pending').order_by(BatchIssuance.requested_at.desc()).all()
    
    # Get recent decisions
    recent_decisions = IssuanceRequest.query.filter(
        IssuanceRequest.status.in_(['approved', 'denied'])
    ).order_by(IssuanceRequest.reviewed_at.desc()).limit(10).all()
    
    # Get recent batch decisions
    recent_batch_decisions = BatchIssuance.query.filter(
        BatchIssuance.status.in_(['approved', 'denied'])
    ).order_by(BatchIssuance.approved_at.desc()).limit(10).all()
    
    return render_template('approval_dashboard.html',
                         pending_requests=pending_requests,
                         pending_batch_requests=pending_batch_requests,
                         recent_decisions=recent_decisions,
                         recent_batch_decisions=recent_batch_decisions)

@app.route('/process_approval', methods=['POST'])
@login_required
def process_approval():
    if current_user.role != 'site_engineer':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    request_id = request.form.get('request_id')
    action = request.form.get('action')
    review_notes = request.form.get('review_notes')
    
    if not request_id or action not in ['approve', 'deny']:
        flash('Invalid request', 'error')
        return redirect(url_for('approval_dashboard'))
    
    try:
        issuance_request = IssuanceRequest.query.get_or_404(request_id)
        
        if issuance_request.status != 'pending':
            flash('Request already processed', 'warning')
            return redirect(url_for('approval_dashboard'))
        
        issuance_request.status = 'approved' if action == 'approve' else 'denied'
        issuance_request.reviewed_by = current_user.username
        issuance_request.reviewed_at = datetime.utcnow()
        issuance_request.review_notes = review_notes
        
        db.session.commit()
        
        # If approved, automatically create the issuance log
        if action == 'approve':
            # Create issuance log
            issuance_log = IssuanceLog(
                request_id=issuance_request.id,
                material_name=issuance_request.material_name,
                quantity_issued=issuance_request.quantity_requested,
                unit=issuance_request.unit,
                issued_by=issuance_request.requested_by,
                authorized_by=current_user.username,
                notes=f"Approved request: {review_notes}" if review_notes else "Approved request"
            )
            db.session.add(issuance_log)
            
            # Update Excel stock
            excel_manager = ExcelManager()
            excel_manager.record_issuance(
                issuance_request.material_name,
                issuance_request.quantity_requested,
                issuance_request.unit,
                current_user.username,
                f"Authorized by {current_user.username}"
            )
            
            db.session.commit()
        
        flash(f'Request {action}d successfully', 'success')
        logging.info(f"Request {action}d: {current_user.username} {action}d {issuance_request.material_name} request from {issuance_request.requested_by}")
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error processing approval: {str(e)}")
        flash('Error processing request. Please try again.', 'error')
    
    return redirect(url_for('approval_dashboard'))

@app.route('/process_batch_approval', methods=['POST'])
@login_required
def process_batch_approval():
    if current_user.role != 'site_engineer':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    batch_id = request.form.get('batch_id')
    action = request.form.get('action')
    review_notes = request.form.get('review_notes')
    
    if not batch_id or action not in ['approve', 'deny']:
        flash('Invalid request', 'error')
        return redirect(url_for('approval_dashboard'))
    
    try:
        batch_issuance = BatchIssuance.query.filter_by(batch_id=batch_id).first()
        
        if not batch_issuance:
            flash('Batch request not found', 'error')
            return redirect(url_for('approval_dashboard'))
        
        if batch_issuance.status != 'pending':
            flash('Batch request already processed', 'warning')
            return redirect(url_for('approval_dashboard'))
        
        batch_issuance.status = 'approved' if action == 'approve' else 'denied'
        batch_issuance.approved_by = current_user.username
        batch_issuance.approved_at = datetime.utcnow()
        batch_issuance.notes = review_notes
        
        db.session.commit()
        
        # If approved, automatically create the issuance logs for all items
        if action == 'approve':
            batch_items = BatchIssuanceItem.query.filter_by(batch_id=batch_id).all()
            excel_manager = ExcelManager()
            
            for item in batch_items:
                # Create issuance log
                issuance_log = IssuanceLog(
                    batch_id=batch_id,
                    material_name=item.material_name,
                    quantity_issued=item.quantity_requested,
                    unit=item.unit,
                    issued_by=batch_issuance.requested_by,
                    authorized_by=current_user.username,
                    notes=f"Batch {batch_id} approved: {review_notes}" if review_notes else f"Batch {batch_id} approved"
                )
                db.session.add(issuance_log)
                
                # Update Excel stock
                excel_manager.record_issuance(
                    item.material_name,
                    item.quantity_requested,
                    item.unit,
                    current_user.username,
                    f"Batch {batch_id} - Authorized by {current_user.username}"
                )
            
            # Update batch status to issued
            batch_issuance.status = 'issued'
            batch_issuance.issued_at = datetime.utcnow()
            
            db.session.commit()
        
        flash(f'Batch request {action}d successfully', 'success')
        logging.info(f"Batch {action}d: {current_user.username} {action}d batch {batch_id} from {batch_issuance.requested_by}")
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error processing batch approval: {str(e)}")
        flash('Error processing batch request. Please try again.', 'error')
    
    return redirect(url_for('approval_dashboard'))

@app.route('/daily_report')
@login_required
def daily_report():
    from datetime import datetime, date
    from sqlalchemy import func
    
    # Get selected date (default to today)
    report_date = request.args.get('report_date')
    if report_date:
        try:
            selected_date = datetime.strptime(report_date, '%Y-%m-%d').date()
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()
    
    # Get daily issuances
    daily_issuances = IssuanceLog.query.filter(
        func.date(IssuanceLog.issued_at) == selected_date
    ).order_by(IssuanceLog.issued_at.desc()).all()
    
    # Calculate summary stats
    total_issuances = len(daily_issuances)
    unique_materials = len(set(log.material_name for log in daily_issuances))
    authorized_count = len([log for log in daily_issuances if log.authorized_by])
    
    # Material summary
    material_summary = db.session.query(
        IssuanceLog.material_name,
        IssuanceLog.unit,
        func.sum(IssuanceLog.quantity_issued).label('total_quantity'),
        func.count(IssuanceLog.id).label('issue_count')
    ).filter(
        func.date(IssuanceLog.issued_at) == selected_date
    ).group_by(IssuanceLog.material_name, IssuanceLog.unit).all()
    
    return render_template('daily_report.html',
                         daily_issuances=daily_issuances,
                         material_summary=material_summary,
                         selected_date=selected_date.strftime('%Y-%m-%d'),
                         total_issuances=total_issuances,
                         unique_materials=unique_materials,
                         authorized_count=authorized_count)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

def generate_batch_id():
    """Generate a unique batch ID"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"BTH-{timestamp}-{random_suffix}"

@app.route('/batch_issuance')
@login_required
def batch_issuance():
    if current_user.role != 'storesperson':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get current stock for the form
    try:
        excel_manager = ExcelManager()
        current_stock = excel_manager.get_current_stock()
        
        # Get recent batch requests
        batch_requests = BatchIssuance.query.filter_by(
            requested_by=current_user.username
        ).order_by(BatchIssuance.requested_at.desc()).limit(10).all()
        
        return render_template('batch_issuance.html', 
                             current_stock=current_stock,
                             batch_requests=batch_requests)
    except Exception as e:
        logging.error(f"Error loading batch issuance: {str(e)}")
        flash('Error loading data', 'error')
        return render_template('batch_issuance.html', current_stock=[], batch_requests=[])

@app.route('/create_batch_request', methods=['POST'])
@login_required
def create_batch_request():
    if current_user.role != 'storesperson':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    # Get form data
    issued_to = request.form.get('issued_to')
    truck_number = request.form.get('truck_number')
    driver_name = request.form.get('driver_name')
    driver_contact = request.form.get('driver_contact')
    notes = request.form.get('notes', '')
    
    # Get materials data
    materials = []
    i = 0
    while request.form.get(f'material_name_{i}'):
        material_name = request.form.get(f'material_name_{i}')
        quantity = request.form.get(f'quantity_{i}')
        unit = request.form.get(f'unit_{i}')
        
        if material_name and quantity and unit:
            try:
                quantity = float(quantity)
                if quantity > 0:
                    materials.append({
                        'name': material_name,
                        'quantity': quantity,
                        'unit': unit
                    })
            except ValueError:
                flash(f'Invalid quantity for {material_name}', 'error')
                return redirect(url_for('batch_issuance'))
        i += 1
    
    if not issued_to or not materials:
        flash('Please fill in all required fields and add at least one material', 'error')
        return redirect(url_for('batch_issuance'))
    
    # Handle GTV image upload
    gtv_image = None
    if 'gtv_image' in request.files:
        file = request.files['gtv_image']
        if file and file.filename != '' and allowed_file(file.filename):
            gtv_image = secure_filename(file.filename)
            gtv_image = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{gtv_image}"
            file.save(os.path.join('uploads', gtv_image))
    
    # Generate batch ID
    batch_id = generate_batch_id()
    
    # Create batch issuance
    batch_issuance = BatchIssuance(
        batch_id=batch_id,
        issued_to=issued_to,
        truck_number=truck_number,
        driver_name=driver_name,
        driver_contact=driver_contact,
        gtv_image=gtv_image,
        requested_by=current_user.username,
        notes=notes
    )
    
    db.session.add(batch_issuance)
    
    # Add batch items
    for material in materials:
        batch_item = BatchIssuanceItem(
            batch_id=batch_id,
            material_name=material['name'],
            quantity_requested=material['quantity'],
            unit=material['unit']
        )
        db.session.add(batch_item)
    
    db.session.commit()
    
    flash(f'Batch request {batch_id} created successfully and sent for approval', 'success')
    return redirect(url_for('batch_issuance'))

@app.route('/stock_report')
@login_required
def stock_report():
    """Generate printable stock report"""
    try:
        excel_manager = ExcelManager()
        current_stock = excel_manager.get_current_stock()
        
        # Get recent issuances for context
        recent_issuances = IssuanceLog.query.order_by(IssuanceLog.issued_at.desc()).limit(20).all()
        
        # Check if this is a print request
        print_mode = request.args.get('print') == 'true'
        
        return render_template('stock_report.html',
                             current_stock=current_stock,
                             recent_issuances=recent_issuances,
                             print_mode=print_mode,
                             report_date=datetime.now())
    except Exception as e:
        logging.error(f"Error generating stock report: {str(e)}")
        flash('Error generating stock report', 'error')
        return redirect(url_for('materials_dashboard'))
