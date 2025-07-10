# Construction Site Material Tracker

A web-based MVP application for tracking construction site materials using photo uploads and OCR (Optical Character Recognition) technology.

## Features

- **Role-based Authentication**: Simple login system for Site Engineers and Storekeepers
- **Photo Upload & OCR**: Upload photos of materials and automatically extract material names and quantities
- **Material Management**: Review, edit, and confirm extracted material data
- **Inventory Tracking**: Real-time stock level monitoring with Excel-based storage
- **Issuance Logging**: Record material issuances with automatic stock updates
- **Mobile-friendly**: Responsive design optimized for mobile devices
- **Excel Integration**: Data stored in Excel format (.xlsx) for easy export and analysis

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Database**: SQLite (for user management and logs)
- **OCR**: Tesseract OCR via pytesseract
- **Excel**: openpyxl for Excel file management
- **Image Processing**: Pillow (PIL)

## Installation & Setup

### Prerequisites

1. **Python 3.7+** installed on your system
2. **Tesseract OCR** binary installed:
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt-get update
   sudo apt-get install tesseract-ocr
   ```
   
   **macOS:**
   ```bash
   brew install tesseract
   ```
   
   **Windows:**
   Download from: https://github.com/UB-Mannheim/tesseract/wiki
   
   **Replit:**
   Tesseract is pre-installed in most Replit environments.

### Setup Instructions

1. **Clone or download the project files**

2. **Install Python dependencies:**
   ```bash
   pip install flask flask-sqlalchemy flask-login pytesseract pillow openpyxl pandas werkzeug
   ```

3. **Set environment variables** (optional):
   ```bash
   export SESSION_SECRET="your-secret-key-here"
   export DATABASE_URL="sqlite:///construction_tracker.db"
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

5. **Access the application:**
   Open your browser and navigate to `http://localhost:5000`

## Usage

### Default Login Credentials

The application comes with two pre-configured demo accounts:

- **Site Engineer**
  - Username: `engineer`
  - Password: `engineer123`

- **Storesperson**
  - Username: `storesperson`
  - Password: `store123`

### Workflow

#### For Site Engineers:
1. Login with engineer credentials
2. Upload a photo of materials on site
3. Review the OCR-extracted material data
4. Edit/confirm material names, quantities, and units
5. Submit to add materials to inventory

#### For Storekeepers:
1. Login with storesperson credentials
2. View current stock levels
3. Select materials to issue
4. Enter quantity to issue and optional notes
5. Submit to record issuance and update stock

### Photo Guidelines

For best OCR results:
- ✅ Ensure good lighting
- ✅ Include material labels/tags in the photo
- ✅ Keep text readable and clear
- ✅ Avoid blurry or distorted images
- ✅ Include quantity information visible in the image

## File Structure

