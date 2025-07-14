#!/usr/bin/env python3
"""
Setup script for Construction Site Material Tracker
"""
import os
import sys
from app import app, db
from bulk_materials_import import import_materials

def setup_database():
    """Initialize database tables and import sample data"""
    print("Setting up database...")
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database tables created")
        
        # Import sample materials
        try:
            import_materials()
            print("✓ Sample materials imported")
        except Exception as e:
            print(f"⚠ Materials import failed: {e}")
            print("  You can manually run: python bulk_materials_import.py")

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ['DATABASE_URL', 'SESSION_SECRET']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables before running the application:")
        print("export DATABASE_URL='postgresql://user:password@localhost/dbname'")
        print("export SESSION_SECRET='your-secret-key-here'")
        return False
    
    print("✓ Environment variables configured")
    return True

def check_dependencies():
    """Check if system dependencies are available"""
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        print("✓ Tesseract OCR is available")
    except Exception as e:
        print(f"⚠ Tesseract OCR not found: {e}")
        print("  Install with: sudo apt-get install tesseract-ocr")
        print("  Or on macOS: brew install tesseract")

def main():
    """Main setup function"""
    print("=== Construction Site Material Tracker Setup ===\n")
    
    # Check dependencies
    check_dependencies()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Setup database
    setup_database()
    
    print("\n=== Setup Complete ===")
    print("You can now run the application with:")
    print("  python main.py")
    print("or")
    print("  gunicorn --bind 0.0.0.0:5000 main:app")
    print("\nDemo accounts:")
    print("  Site Engineer: engineer1/engineer123")
    print("  Storesman: storesman1/store123")

if __name__ == "__main__":
    main()