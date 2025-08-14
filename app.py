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

# Database configuration for Render
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    # Fallback for local development
    db_url = "sqlite:///construction_tracker.db"
    logging.warning("No DATABASE_URL found, using SQLite fallback")
elif db_url.startswith("postgres://"):
    # Fix Heroku/Render postgres URL format
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
logging.info(f"Database configured: {db_url[:50]}...")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Enhanced database configuration for production
if db_url and 'postgresql' in db_url:
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        'pool_pre_ping': True,
        "pool_recycle": 300,
        "pool_timeout": 30,
        "max_overflow": 10,
        "connect_args": {
            "sslmode": "require",
            "connect_timeout": 30
        }
    }
else:
    # SQLite configuration for local development
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        'pool_pre_ping': True,
        "pool_recycle": 300,
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

# Create tables
with app.app_context():
    import models_new  # noqa: F401
    db.create_all()
    logging.info("Database tables created")
