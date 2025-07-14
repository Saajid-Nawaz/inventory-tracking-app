# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-07-14

### Added
- Complete multi-site inventory management system
- Role-based access control (Site Engineers and Storesmen)
- FIFO inventory valuation and cost tracking
- Material categorization system with 17 comprehensive categories
- SKU management with auto-generation (MAT-XXXX format)
- Real-time stock level monitoring with minimum level alerts
- Photo upload and OCR processing for material identification
- Approval workflows for material requests and transfers
- Comprehensive reporting system (PDF and Excel export)
- Document upload support for receipts and supporting materials
- Bulk material import functionality via Excel
- Stock transfer capabilities between sites
- Complete audit trail for all transactions
- Mobile-responsive Bootstrap 5 interface
- Production-ready PostgreSQL database implementation
- Gunicorn server configuration for deployment

### Technical Features
- Flask 3.1.1 web framework
- PostgreSQL database with SQLAlchemy ORM
- Flask-Login authentication system
- pytesseract OCR integration
- ReportLab PDF generation
- openpyxl Excel file processing
- Comprehensive error handling and logging
- Security features including file upload validation

### Database Schema
- Users table with role-based permissions
- Sites table for multi-site management
- Materials table with categorization and SKU system
- Transactions table for FIFO inventory tracking
- Issue requests and approval workflow tables
- Stock levels and transfer request tables
- Complete relational database design

### Initial Data
- 8 core construction materials with proper categorization
- 5 demo user accounts (2 Site Engineers, 3 Storesmen)
- 3 sample construction sites
- 29 sample transactions for demonstration
- Comprehensive material categories and units