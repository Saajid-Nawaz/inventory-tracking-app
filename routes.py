import os
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from PIL import Image
import logging

from app import app, db
from models import User, MaterialRecord, IssuanceLog
from ocr_processor import extract_materials_from_image
from excel_manager import ExcelManager

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
        
        return render_template('storesperson.html', 
                             current_stock=current_stock, 
                             recent_issuances=recent_issuances)
    except Exception as e:
        logging.error(f"Error reading Excel file: {str(e)}")
        flash('Error reading stock data', 'error')
        return render_template('storesperson.html', current_stock=[], recent_issuances=[])

@app.route('/issue_materials', methods=['POST'])
@login_required
def issue_materials():
    if current_user.role != 'storesperson':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    material_name = request.form.get('material_name')
    quantity_issued = request.form.get('quantity_issued')
    unit = request.form.get('unit')
    notes = request.form.get('notes', '')
    
    if not all([material_name, quantity_issued, unit]):
        flash('All fields are required', 'error')
        return redirect(url_for('storesperson'))
    
    try:
        quantity_issued = float(quantity_issued)
    except ValueError:
        flash('Invalid quantity', 'error')
        return redirect(url_for('storesperson'))
    
    # Check if sufficient stock is available
    try:
        excel_manager = ExcelManager()
        current_stock = excel_manager.get_current_stock()
        
        stock_item = next((item for item in current_stock if item['material_name'] == material_name), None)
        if not stock_item:
            flash('Material not found in stock', 'error')
            return redirect(url_for('storesperson'))
        
        if stock_item['quantity'] < quantity_issued:
            flash(f'Insufficient stock. Available: {stock_item["quantity"]} {unit}', 'error')
            return redirect(url_for('storesperson'))
        
        # Record issuance
        issuance = IssuanceLog(
            material_name=material_name,
            quantity_issued=quantity_issued,
            unit=unit,
            issued_by=current_user.username,
            notes=notes
        )
        db.session.add(issuance)
        db.session.commit()
        
        # Update Excel file
        excel_manager.record_issuance(material_name, quantity_issued, unit, current_user.username, notes)
        
        flash(f'Successfully issued {quantity_issued} {unit} of {material_name}', 'success')
        
    except Exception as e:
        logging.error(f"Error processing issuance: {str(e)}")
        flash('Error processing issuance', 'error')
    
    return redirect(url_for('storesperson'))

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
    return render_template('500.html'), 500
