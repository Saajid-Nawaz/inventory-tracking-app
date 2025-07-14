# Construction Site Material Tracker

A comprehensive web-based inventory tracking and approval system for construction sites with multi-site management capabilities.

## Features

### 🏗️ Multi-Site Management
- Manage inventory across multiple construction sites
- Site-specific stock tracking and reporting
- Inter-site material transfer capabilities

### 👥 Role-Based Access Control
- **Site Engineers**: Manage multiple sites, approve material requests, oversee inventory
- **Storesmen**: Site-specific access, material requests, stock management

### 📊 Advanced Inventory Management
- FIFO (First-In-First-Out) inventory valuation
- Real-time stock level monitoring
- Minimum stock level alerts and notifications
- Comprehensive material categorization (17 categories)
- SKU management system with auto-generation

### 📱 Mobile-Friendly Interface
- Responsive Bootstrap 5 design
- Photo upload and OCR processing for material identification
- Mobile-optimized dashboards and forms

### 📋 Approval Workflows
- Material issue request system
- Batch material issuance with approval workflow
- Stock transfer requests between sites
- Complete audit trail for all transactions

### 📈 Reporting & Analytics
- PDF and Excel report generation
- Daily issues reports
- Stock summary reports
- Transaction history with filtering
- Cost tracking and valuation reports

### 🔐 Security Features
- Session-based authentication
- Role-based permission system
- File upload validation and sanitization
- Secure document storage

## Technology Stack

- **Backend**: Python 3.11, Flask
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login
- **Frontend**: Bootstrap 5, HTML5, JavaScript
- **File Processing**: Pillow, pytesseract (OCR)
- **Reports**: ReportLab (PDF), openpyxl (Excel)
- **Server**: Gunicorn

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL database
- Tesseract OCR (for image processing)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd construction-inventory-tracker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost/dbname"
   export SESSION_SECRET="your-secret-key-here"
   ```

4. **Initialize the database**
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

5. **Import sample materials (optional)**
   ```bash
   python bulk_materials_import.py
   ```

6. **Run the application**
   ```bash
   python main.py
   ```

The application will be available at `http://localhost:5000`

## Demo Accounts

### Site Engineers
- **Username**: `engineer1` | **Password**: `engineer123`
- **Username**: `engineer2` | **Password**: `engineer123`

### Storesmen
- **Username**: `storesman1` | **Password**: `store123`
- **Username**: `storesman2` | **Password**: `store123`
- **Username**: `storesman3` | **Password**: `store123`

## Project Structure

```
├── app.py                 # Main Flask application setup
├── main.py                # Application entry point
├── models_new.py          # Database models
├── routes_new.py          # Web routes and API endpoints
├── inventory_service.py   # Business logic for inventory management
├── report_generator.py    # PDF and Excel report generation
├── excel_manager.py       # Excel file operations
├── ocr_processor.py       # Photo processing and OCR
├── bulk_materials_import.py # Material database initialization
├── templates/             # HTML templates
├── static/               # CSS and JavaScript files
├── uploads/              # File storage directory
└── data/                 # Sample data and configurations
```

## Key Features Explained

### FIFO Inventory Valuation
The system implements proper First-In-First-Out inventory accounting, ensuring accurate cost tracking and valuation of materials as they are received and issued.

### Multi-Site Architecture
- Each site operates independently with its own inventory
- Materials can be transferred between sites with proper approval workflows
- Site-specific reporting and analytics

### Role-Based Permissions
- **Site Engineers**: Full system access, can manage multiple sites, approve requests
- **Storesmen**: Site-specific access, can request materials, manage stock levels

### Material Categories
The system supports 17 comprehensive categories:
- Aggregates, Construction, Electrical, Finishing, Hardware
- Masonry, Plumbing, Roofing, Timber, Safety, Insulation
- Gardening, Landscaping, Flooring, HVAC, Tools, General

## Production Deployment

### Environment Configuration
- Set `DATABASE_URL` to your PostgreSQL connection string
- Set `SESSION_SECRET` to a secure random string
- Ensure Tesseract OCR is installed on the system

### Recommended Production Setup
- Use Gunicorn as the WSGI server
- Configure PostgreSQL with connection pooling
- Set up proper file storage (consider cloud storage for uploads)
- Configure logging and monitoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please create an issue in the GitHub repository.

---

**Built with ❤️ for construction site management**