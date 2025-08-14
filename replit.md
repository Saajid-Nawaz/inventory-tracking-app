# Construction Site Material Tracker

## Overview
This project is a web-based MVP application designed to track construction site materials. It leverages photo uploads and OCR technology for automatic material information extraction, enabling site engineers to log materials and storekeepers to manage inventory, issuances, and transactions. The vision is to provide an enterprise-level inventory management solution with multi-site support, real-time stock monitoring, and comprehensive reporting capabilities.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture
The application employs a traditional three-tier architecture:
-   **Presentation Layer**: HTML5 templates with Bootstrap 5 for responsive design.
-   **Business Logic Layer**: Flask web framework (Python backend).
-   **Data Storage Layer**: PostgreSQL database for all persistent data.

### Key Architectural Decisions
-   **Flask Framework**: Chosen for its simplicity and ecosystem, suitable for MVP development.
-   **Full Database Storage**: All data, including inventory, transactions, user management, and logs, are stored in PostgreSQL.
-   **Server-side OCR**: Tesseract OCR processing is handled on the backend.
-   **Role-based Access**: A two-role system (Site Engineer/Storesperson) with session-based authentication.
-   **Multi-Site Inventory Management**: Supports multiple construction sites with site-specific inventory tracking and data isolation for storesmen.
-   **FIFO Inventory Valuation**: Implements First-In-First-Out cost accounting for accurate inventory valuation.
-   **Advanced Transaction System**: All inventory movements are tracked with unique serial numbers and a complete audit trail.
-   **Modern Dashboard UI**: Redesigned UI with card-based layouts, advanced animations, and responsive design.
-   **Comprehensive Material Catalog**: Includes material categorization and an extensive database of construction materials with standardized units and specifications.
-   **Professional Report System**: Enhanced PDF and Excel reports with company branding, consistent styling, and comprehensive data presentation.
-   **Render Deployment Ready**: Fully configured for deployment to Render cloud platform with PostgreSQL database integration.
-   **Successfully Deployed**: Live application deployed at https://inventory-tracking-y2pg.onrender.com with all features operational.

### Key Components
-   **Flask Application**: Main application configuration, database initialization, file upload, and session management.
-   **Models**: SQLAlchemy ORM for User, MaterialRecord, IssuanceRequest, IssuanceLog, and Transaction models, supporting detailed relationships for multi-site operations.
-   **Routes**: Handles authentication, role-based dashboards, photo processing, material management, and all inventory workflows.
-   **OCR Processor**: Integrates Tesseract for text extraction and pattern matching from images.
-   **Excel Manager**: Manages Excel file operations for import/export.
-   **Inventory Service Layer**: Centralized business logic for all inventory operations, including FIFO calculations.
-   **Report Generation Service**: Automated PDF and Excel report generation with professional company branding.
-   **Enhanced Professional Reports**: Professional report generator with company branding, modern styling, and comprehensive data presentation.
-   **Deployment Configuration**: Complete Render deployment setup with gunicorn, PostgreSQL integration, and production optimizations.

## External Dependencies
### Python Packages
-   Flask
-   Flask-SQLAlchemy
-   Flask-Login
-   pytesseract
-   openpyxl
-   Pillow
-   pandas
-   Werkzeug (for password hashing)

### System Dependencies
-   Tesseract OCR binary

### Frontend Dependencies
-   Bootstrap 5 (CDN)
-   Font Awesome (CDN)
-   jQuery
-   Chart.js (for data visualization)