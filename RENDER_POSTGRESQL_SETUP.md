# Render PostgreSQL Setup Guide

## Updated Configuration for Native Render Database

Your application has been updated to work seamlessly with Render's native PostgreSQL service. The configuration automatically handles:

- Database URL format conversion (postgres:// → postgresql://)
- Optimized connection pooling for Render's infrastructure
- SSL requirements and security settings
- Automatic fallback for local development

## Deployment Steps

### 1. Push Updated Code
```bash
git add .
git commit -m "Configure for Render PostgreSQL"
git push origin main
```

### 2. Deploy via Render Dashboard
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically:
   - Create the web service
   - Create the PostgreSQL database
   - Link them together
   - Set all environment variables

### 3. Verify Deployment
- Your service will be available at: `https://construction-material-tracker.onrender.com`
- Database will be automatically provisioned and connected
- All features will work immediately

## What's Configured

### Database Settings
- **Service**: Native Render PostgreSQL (Free Tier)
- **Database Name**: `construction_tracker`
- **Connection**: Automatic via environment variables
- **SSL**: Required and configured
- **Pooling**: Optimized for Render infrastructure

### Environment Variables (Auto-Generated)
- `DATABASE_URL`: PostgreSQL connection string
- `SESSION_SECRET`: Flask session encryption
- `FLASK_ENV`: Production mode
- `PYTHONPATH`: Application path

### File Storage
- **Upload Directory**: `/opt/render/project/src/uploads`
- **Storage Size**: 10GB persistent disk
- **Mount Path**: Automatically configured

## Features Available After Deployment
✅ Multi-site inventory management
✅ Role-based access control
✅ Professional PDF/Excel reports
✅ OCR receipt processing
✅ Real-time stock tracking
✅ Material request workflows
✅ Stock transfer management
✅ ZMW currency support
✅ Bulk import/export capabilities

## Database Connection Benefits
- **Automatic SSL**: Secure connections enabled
- **Connection Pooling**: Optimized for performance
- **Error Recovery**: Built-in reconnection logic
- **Monitoring**: Render provides database metrics
- **Backups**: Automatic daily backups included

## No Manual Configuration Required
The render.yaml blueprint handles everything automatically:
- Database creation
- Service linking
- Environment variable setup
- SSL certificate provisioning
- Domain assignment

Your application will be production-ready immediately after deployment with full PostgreSQL functionality.