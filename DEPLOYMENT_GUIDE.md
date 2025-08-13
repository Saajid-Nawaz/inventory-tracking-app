# Deployment Guide - Construction Material Tracker on Render

## Overview
This guide explains how to deploy the comprehensive Construction Site Material Tracker to Render while maintaining all functionality including multi-site management, role-based access, inventory tracking, and reporting capabilities.

## Prerequisites
- Render account (render.com)
- GitHub repository with this codebase

## Step 1: Prepare for Deployment

### 1. Update requirements.txt
Copy the contents from `requirements_render.txt` to your main `requirements.txt` file:

```bash
cp requirements_render.txt requirements.txt
```

### 2. Environment Variables Required
- `DATABASE_URL` - Automatically set by Render PostgreSQL
- `SESSION_SECRET` - Generate a secure secret key

## Step 2: Database Setup

### 1. Create PostgreSQL Database
1. In Render dashboard, click "New +"
2. Select "PostgreSQL"
3. Choose "Free" plan
4. Name: `construction-tracker-db`
5. Database Name: `construction_tracker`
6. Click "Create Database"

## Step 3: Web Service Setup

### 1. Create Web Service
1. In Render dashboard, click "New +"
2. Select "Web Service"
3. Connect your GitHub repository
4. Configure:
   - Name: `construction-material-tracker`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT main:app`

### 2. Environment Variables
Set these in Render dashboard:
- `DATABASE_URL`: Link to your PostgreSQL database
- `SESSION_SECRET`: Generate a random secret key
- `FLASK_ENV`: `production`

### 3. Advanced Settings
- Auto-Deploy: `Yes`
- Health Check Path: `/` (optional)

## Step 4: Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Build the application
   - Install dependencies
   - Connect to PostgreSQL
   - Initialize database tables
   - Load sample data
   - Start the application

## Step 5: Post-Deployment Setup

### 1. Access the Application
- Your app will be available at: `https://your-app-name.onrender.com`
- First load may take 30-60 seconds (cold start)

### 2. Default Login Credentials
The system creates these default users:
- **Site Engineer**: `engineer1` / `engineer123`
- **Site Engineer**: `engineer2` / `engineer123`
- **Storesman (Main Site)**: `storesman1` / `storesman123`
- **Storesman (North Warehouse)**: `storesman2` / `storesman123`
- **Storesman (South Depot)**: `storesman3` / `storesman123`

### 3. Test Key Features
1. **Login System**: Test both engineer and storesman roles
2. **Multi-Site Access**: Verify site isolation for storesmen
3. **Material Management**: Add/edit materials and stock levels
4. **Inventory Tracking**: Test material receipts and issues
5. **Reporting**: Generate PDF and Excel reports
6. **File Uploads**: Test document uploads and image processing

## Features Maintained in Production

✅ **Complete Multi-Site Management**
- 3 default sites with proper isolation
- Site-specific inventory tracking
- Cross-site stock transfers with approval

✅ **Role-Based Access Control**
- Site Engineers: Full system access
- Storesmen: Site-specific access only
- Complete data isolation between sites

✅ **Comprehensive Inventory System**
- 94+ construction materials across 12 categories
- FIFO inventory valuation
- Real-time stock level tracking
- Minimum level alerts

✅ **Advanced Transaction Management**
- Complete audit trail for all inventory movements
- Authorization workflow for material issues
- Batch processing capabilities
- Supporting document uploads

✅ **Production-Ready Reporting**
- PDF report generation
- Excel export functionality
- ZMW currency formatting
- Site-specific and comprehensive reports

✅ **File Management System**
- Document uploads for receipts/invoices
- Image processing for material photos
- Secure file storage and access

## Scaling Considerations

### Database
- Free PostgreSQL: 1GB storage, good for MVP
- Upgrade to paid plans for production use
- Automatic backups included

### Storage
- Render provides 10GB disk storage
- File uploads stored in `/opt/render/project/src/uploads`
- Consider cloud storage (S3) for larger deployments

### Performance
- Free tier: 512MB RAM, shared CPU
- Upgrade to paid plans for better performance
- Auto-scaling available on paid plans

## Monitoring and Maintenance

### Health Monitoring
- Render provides built-in monitoring
- Application logs available in dashboard
- Set up alerts for downtime

### Database Maintenance
- Monitor storage usage
- Regular backups (automatic on Render)
- Performance optimization as needed

### Updates
- Auto-deploy from GitHub on push
- Manual deploys available
- Zero-downtime deployments

## Security Notes

✅ **Production Security Measures**
- HTTPS enforced by Render
- Database connections encrypted
- Session security with secure secrets
- File upload validation and sanitization
- SQL injection protection via SQLAlchemy ORM

## Support and Troubleshooting

### Common Issues
1. **Cold Starts**: First request may be slow (30-60s)
2. **File Uploads**: Ensure proper permissions and storage
3. **Database Connections**: Monitor connection limits

### Logs and Debugging
- Access logs via Render dashboard
- Set logging level in environment variables
- Monitor application performance

This deployment maintains all features of the comprehensive inventory system while being production-ready on Render's platform.