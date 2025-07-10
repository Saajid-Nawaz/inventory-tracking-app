# Construction Site Material Tracker

## Overview

This is a web-based MVP application for tracking construction site materials using photo uploads and OCR (Optical Character Recognition) technology. The system enables site engineers to capture photos of materials on-site and automatically extract material information, while storekeepers can manage inventory levels and track material issuances.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a traditional three-tier architecture:

1. **Presentation Layer**: HTML5 templates with Bootstrap 5 for responsive design
2. **Business Logic Layer**: Flask web framework with Python backend
3. **Data Storage Layer**: SQLite database for user management and Excel files for material data

### Key Architectural Decisions

- **Flask over FastAPI**: Chosen for its simplicity and extensive ecosystem, suitable for MVP development
- **Hybrid Data Storage**: SQLite for user authentication and logs, Excel files for material data to enable easy export and analysis
- **Server-side OCR**: Tesseract OCR processing on the backend to avoid client-side dependencies
- **Role-based Access**: Simple two-role system (Site Engineer/Storesperson) with session-based authentication

## Key Components

### Backend Components

1. **Flask Application** (`app.py`):
   - Main application configuration
   - Database initialization with SQLAlchemy
   - File upload and session management

2. **Models** (`models.py`):
   - User model for authentication
   - MaterialRecord model for tracking materials
   - IssuanceLog model for recording material distributions

3. **Routes** (`routes.py`):
   - Authentication endpoints
   - Role-based dashboards
   - Photo upload and processing workflows
   - Material management endpoints

4. **OCR Processor** (`ocr_processor.py`):
   - Tesseract OCR integration
   - Text extraction from images
   - Pattern matching for material identification

5. **Excel Manager** (`excel_manager.py`):
   - Excel file operations using openpyxl
   - Stock level management
   - Issuance logging

### Frontend Components

1. **Templates**:
   - Base template with Bootstrap 5 integration
   - Role-specific dashboards
   - Material preview and confirmation forms

2. **Static Assets**:
   - Custom CSS for mobile optimization
   - JavaScript for form validation and UI enhancements

## Data Flow

1. **Material Recording Flow**:
   - Site Engineer uploads photo → OCR processing → Material extraction → User review → Confirmation → Excel storage

2. **Issuance Flow**:
   - Storesperson views current stock → Selects materials → Records issuance → Updates stock levels → Logs transaction

3. **Authentication Flow**:
   - User login → Role verification → Dashboard redirection → Session management

## External Dependencies

### Python Packages
- Flask: Web framework
- Flask-SQLAlchemy: Database ORM
- Flask-Login: User session management
- pytesseract: OCR processing
- openpyxl: Excel file manipulation
- Pillow: Image processing
- pandas: Data manipulation

### System Dependencies
- Tesseract OCR binary (system-level installation required)

### Frontend Dependencies
- Bootstrap 5 (CDN): UI framework
- Font Awesome (CDN): Icons
- jQuery (implied): JavaScript utilities

## Deployment Strategy

### Local Development
- SQLite database for simplicity
- Local file storage for uploads and Excel files
- Debug mode enabled for development

### Production Considerations
- Environment-based configuration using os.environ
- ProxyFix middleware for proper request handling
- File upload size limits (16MB)
- Logging configuration for monitoring

### Scalability Notes
- Excel files can be replaced with proper database tables
- File storage can be moved to cloud storage (S3, etc.)
- OCR processing can be moved to cloud services (Google Vision API)
- Database can be upgraded to PostgreSQL for better performance

### Security Considerations
- Password hashing using Werkzeug
- Session management with Flask-Login
- File upload validation and sanitization
- Directory traversal protection with secure_filename

The application is designed as an MVP with clear upgrade paths for production deployment, including database migration strategies and cloud service integration options.