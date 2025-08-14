import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging for production
log_level = logging.INFO if os.environ.get("FLASK_ENV") == "production" else logging.DEBUG
logging.basicConfig(level=log_level)

class Base(DeclarativeBase):
    pass

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-dev-secret-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration for Render
db_url = os.environ.get("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "sqlite:///construction_tracker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'pool_pre_ping': True,
    "pool_recycle": 300,
    "pool_timeout": 20,
    "max_overflow": 0,
}

# File upload configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DATA_FOLDER'] = 'data'

# Ensure upload and data directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DATA_FOLDER'], exist_ok=True)

# Initialize database
db = SQLAlchemy(app, model_class=Base)

# Import models to register them
try:
    from models_new import (
        User, Site, Material, StockLevel, Transaction, IssueRequest, 
        BatchIssueRequest, BatchIssueItem, StockAdjustment, FIFOBatch, 
        StockTransferRequest, SystemSettings
    )
    logging.info("Models imported successfully")
except ImportError as e:
    logging.error(f"Failed to import models: {e}")

# Create tables and initialize data
with app.app_context():
    try:
        db.create_all()
        logging.info("Database tables created")
        
        # Initialize default data if needed
        from inventory_service import initialize_default_data
        initialize_default_data()
        logging.info("Default data initialized successfully")
    except Exception as e:
        logging.error(f"Database initialization error: {e}")

# Import routes
try:
    from routes_deploy import *
    logging.info("Routes loaded successfully")
except ImportError as e:
    logging.error(f"Failed to import routes: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)