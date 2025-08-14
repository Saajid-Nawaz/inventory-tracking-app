"""
Simplified Routes for Deployment
"""

from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app_deploy import app, db
from datetime import datetime
from models_new import User, Site, Material, StockLevel, Transaction

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    """Home page - redirect based on authentication and role"""
    if current_user.is_authenticated:
        if current_user.role == 'site_engineer':
            return redirect(url_for('site_engineer_dashboard'))
        elif current_user.role == 'storesman':
            return redirect(url_for('storesman_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            if user.role == 'site_engineer':
                return redirect(url_for('site_engineer_dashboard'))
            elif user.role == 'storesman':
                return redirect(url_for('storesman_dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/site_engineer/dashboard')
@login_required
def site_engineer_dashboard():
    """Site Engineer Dashboard"""
    if current_user.role != 'site_engineer':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    # Get basic statistics
    total_sites = Site.query.count()
    total_materials = Material.query.count()
    recent_transactions = Transaction.query.order_by(Transaction.timestamp.desc()).limit(10).all()
    
    return render_template('site_engineer_dashboard.html', 
                         total_sites=total_sites,
                         total_materials=total_materials,
                         recent_transactions=recent_transactions)

@app.route('/storesman/dashboard')
@login_required
def storesman_dashboard():
    """Storesman Dashboard"""
    if current_user.role != 'storesman':
        flash('Access denied!', 'error')
        return redirect(url_for('index'))
    
    # Get site-specific data
    site = Site.query.get(current_user.assigned_site_id) if current_user.assigned_site_id else None
    if not site:
        flash('No site assigned!', 'error')
        return redirect(url_for('index'))
    
    # Get materials for this site
    materials = Material.query.all()
    stock_levels = StockLevel.query.filter_by(site_id=site.id).all()
    
    return render_template('storesman_dashboard.html', 
                         site=site,
                         materials=materials,
                         stock_levels=stock_levels,
                         current_time=datetime.now().strftime('%Y-%m-%d %H:%M'))

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

# API endpoints for basic functionality
@app.route('/api/materials')
def api_materials():
    """Get all materials"""
    materials = Material.query.all()
    return jsonify([{
        'id': m.id,
        'name': m.name,
        'unit': m.unit,
        'category': m.category
    } for m in materials])

@app.route('/api/sites')
def api_sites():
    """Get sites based on user role"""
    if current_user.role == 'site_engineer':
        sites = Site.query.all()
    else:
        sites = Site.query.filter_by(id=current_user.assigned_site_id).all()
    
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'location': s.location
    } for s in sites])

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', 
                         error_code=404, 
                         error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', 
                         error_code=500, 
                         error_message="Internal server error"), 500