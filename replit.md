# Construction Site Material Tracker

## Overview

This is a web-based MVP application for tracking construction site materials using photo uploads and OCR (Optical Character Recognition) technology. The system enables site engineers to capture photos of materials on-site and automatically extract material information, while storekeepers can manage inventory levels and track material issuances.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a traditional three-tier architecture:

1. **Presentation Layer**: HTML5 templates with Bootstrap 5 for responsive design
2. **Business Logic Layer**: Flask web framework with Python backend
3. **Data Storage Layer**: PostgreSQL database for all persistent data including inventory, transactions, and user management

### Key Architectural Decisions

- **Flask over FastAPI**: Chosen for its simplicity and extensive ecosystem, suitable for MVP development
- **Full Database Storage**: PostgreSQL database for all data including user authentication, inventory, transactions, and system logs
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
   - IssuanceRequest model for authorization workflow
   - IssuanceLog model for recording material distributions with authorization tracking

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

2. **Authorization & Issuance Flow**:
   - Storesperson requests material issuance → Site Engineer reviews & approves/denies → Auto-issuance on approval → Stock updates → Transaction logging

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
- Full PostgreSQL database implementation provides production-ready data persistence
- File storage can be moved to cloud storage (S3, etc.)
- OCR processing can be moved to cloud services (Google Vision API)
- Database includes proper indexing and relationships for optimal performance

### Security Considerations
- Password hashing using Werkzeug
- Session management with Flask-Login
- File upload validation and sanitization
- Directory traversal protection with secure_filename

## Recent Changes (July 2025)

### Multi-Site Inventory Management System (Complete Rewrite)
- **Database-First Architecture**: Migrated from Excel-based storage to full PostgreSQL database for all inventory data
- **Multi-Site Support**: Complete support for multiple construction sites with site-specific inventory tracking
- **FIFO Inventory Valuation**: Implemented proper FIFO (First-In-First-Out) cost accounting for accurate inventory valuation
- **Enhanced User Management**: Site Engineers can manage multiple sites, Storesmen assigned to specific sites
- **Advanced Transaction System**: All inventory movements tracked with unique serial numbers and complete audit trail
- **Real-time Stock Monitoring**: Live stock level tracking with minimum level alerts and notifications
- **Comprehensive Reporting**: PDF and Excel export capabilities for inventory reports and transaction history

### Latest Enhancements (July 14, 2025)
- **Document Upload Support**: Added supporting document upload functionality for material receipts (invoices, GRVs)
- **Bulk Material Receipt**: Implemented bulk receipt functionality for multiple materials in single transaction
- **Cost Visibility Controls**: Hidden cost/value information from storesman role as per security requirements
- **Enhanced File Management**: Added document viewing and secure file storage for uploaded supporting documents
- **Complete Template System**: All dashboard templates and quick actions now fully functional
- **Role-Based Permission Refinement**: Refined access controls to match exact requirements specifications

### System Diagnosis & Fixes (July 14, 2025)
- **Fixed Missing Sites API**: Added `/api/sites` endpoint for complete API functionality
- **Resolved StockTransferRequest Import**: Fixed missing import causing approve_requests page errors
- **Enhanced Report Generation**: All report types (PDF/Excel) working correctly with ZMW currency formatting
- **Database Integrity Verified**: All 29 transactions, 5 users, 3 sites, 8 materials properly structured
- **Authentication System**: Confirmed login/logout functionality for both Site Engineers and Storesmen
- **Template System**: All critical pages (receive_materials, request_materials, approve_requests) fully functional
- **API Endpoints**: Materials API (8 items), Sites API (3 items), and pending counts API all operational
- **Excel Upload Fix**: Expanded valid units list to include common construction materials units:
  - Added: tonnes, tonner, tonne, EA, each, pieces, meters, metres, litres, cubic meters, square meters
  - Fixed unit validation that was preventing materials with units like 'tonnes', 'tonner', 'EA' from being imported
  - Enhanced error reporting to provide detailed feedback on upload success/failure
  - All previously rejected materials should now import successfully
- **Material Category System**: Comprehensive material categorization system implemented:
  - Added 17 predefined categories: Construction, Masonry, Electrical, Plumbing, Timber, Roofing, Aggregates, Finishing, Gardening, Landscaping, HVAC, Insulation, Flooring, Hardware, Safety, Tools, General
  - Updated database schema to include category field with proper categorization
  - Enhanced material management with category-based filtering and search functionality
  - Excel upload template now includes category column for bulk material categorization
  - All existing materials properly categorized across construction, electrical, plumbing, and other relevant categories
- **Comprehensive Materials Database**: Imported 72 additional construction materials from provided specifications:
  - Total database now contains 94 materials across 14 categories (cleaned up duplicates)
  - Complete coverage of construction needs: Aggregates (10), Construction (14), Electrical (8), Finishing (8), Hardware (11), Masonry (8), Plumbing (9), Roofing (5), Timber (7), Safety (5), Insulation (4), Gardening (3), Landscaping (1), Flooring (1)
  - Includes detailed specifications for rebar sizes, electrical components, plumbing fixtures, safety equipment, and finishing materials
  - All materials have standardized units (tonnes, EA, meters, pieces, bags, etc.), cost data, and minimum stock levels
  - Removed duplicate entries and standardized naming conventions for consistency

### Technical Enhancements
1. **Enhanced Data Models**: Complete restructure with proper relationships for multi-site operations
2. **Inventory Service Layer**: Centralized business logic for all inventory operations with FIFO calculations
3. **Report Generation Service**: Automated PDF and Excel report generation with customizable filters
4. **Role-Based Dashboards**: Separate interfaces optimized for Site Engineers and Storesmen workflows
5. **Stock Adjustment Features**: Physical count reconciliation with automated variance tracking
6. **Batch Processing**: Support for bulk material issue requests with approval workflows

### Data Persistence
- **PostgreSQL Database**: All data including inventory, transactions, users, and system logs stored in database
- **Sample Data Initialization**: Automatic creation of demo sites, materials, and initial inventory on first run
- **No Data Loss**: Complete elimination of memory loss between sessions through proper database storage

The system now provides enterprise-level inventory management capabilities with production-ready data persistence and comprehensive multi-site support.