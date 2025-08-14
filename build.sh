#!/bin/bash

# Install system dependencies for Render deployment
echo "Installing system dependencies..."

# Update package list
apt-get update

# Install Tesseract OCR
apt-get install -y tesseract-ocr tesseract-ocr-eng

# Install Python dependencies
pip install -r requirements.txt

echo "Build completed successfully!"