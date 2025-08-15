import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.INFO)

class Base(DeclarativeBase):
    pass

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration with robust error handling
database_url = os.environ.get("DATABASE_URL")

# Check for the problematic hostname and provide fallback
if database_url and "dpg-d1r5v5be5dus73eaj13g-a" in database_url:
    logging.error("Detected problematic Render database hostname, using fallback")
    database_url = None

if database_url:
    # Convert postgres:// to postgresql:// for SQLAlchemy compatibility
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    try:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
        logging.info(f"Using PostgreSQL database: {database_url[:50]}...")
        
        # Production PostgreSQL configuration optimized for Render
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            'pool_pre_ping': True,
            'pool_recycle': 280,
            'pool_timeout': 20,
            'max_overflow': 0,
            'echo': False,
            'connect_args': {
                'sslmode': 'require',
                'connect_timeout': 10,
                'application_name': 'construction_tracker'
            }
        }
    except Exception as e:
        logging.error(f"PostgreSQL configuration failed: {e}")
        database_url = None

if not database_url:
    # Robust fallback for deployment issues
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///construction_tracker.db"
    logging.warning("Using SQLite fallback - set DATABASE_URL environment variable for PostgreSQL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# File upload configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATA_FOLDER'] = 'data'

# Ensure upload and data directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)

# Initialize database
db = SQLAlchemy(app, model_class=Base)

# Create tables with error handling for production
with app.app_context():
    try:
        import models_new  # noqa: F401
        db.create_all()
        logging.info("Database tables created successfully")
        
        # Initialize default data for new deployments
        from routes_new import initialize_default_data
        initialize_default_data()
        
    except Exception as e:
        logging.error(f"Database initialization error: {str(e)}")
        # Don't fail completely, let the app start and show proper error pages
        pass
