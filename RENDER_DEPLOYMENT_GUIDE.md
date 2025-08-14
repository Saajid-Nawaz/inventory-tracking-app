# Construction Material Tracker - Render Deployment Guide

## Overview
This guide provides step-by-step instructions to deploy the Construction Material Tracker to Render directly from GitHub.

## Prerequisites
1. GitHub account with your project repository
2. Render account (free tier available)
3. Basic understanding of environment variables

## Deployment Steps

### 1. Prepare Your GitHub Repository
Ensure your repository contains these essential files:
- `requirements.txt` - Python dependencies
- `render.yaml` - Render service configuration
- `Procfile` - Process command for web service
- `gunicorn.conf.py` - Gunicorn server configuration
- `main.py` - Application entry point

### 2. Connect to Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" and select "Blueprint"
3. Connect your GitHub account if not already connected
4. Select your repository containing the construction tracker

### 3. Automatic Deployment via render.yaml

The `render.yaml` file will automatically configure:
- **Web Service**: Python web application
- **Database**: PostgreSQL database (free tier)
- **Environment Variables**: Automatically set up
- **File Storage**: 10GB disk for uploads

### 4. Manual Web Service Setup (Alternative)

If you prefer manual setup:

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure the following:

**Basic Settings:**
- Name: `construction-material-tracker`
- Environment: `Python 3`
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn -c gunicorn.conf.py main:app`

**Environment Variables:**
- `DATABASE_URL`: (Will be set automatically when you add database)
- `SESSION_SECRET`: (Generate a random string)
- `FLASK_ENV`: `production`
- `PYTHONPATH`: `/opt/render/project/src`

### 5. Add PostgreSQL Database

1. Click "New +" → "PostgreSQL"
2. Name: `construction-db`
3. Database Name: `construction_tracker`
4. Plan: Free
5. Connect to your web service

### 6. Configure File Storage (Optional)

For file uploads and data storage:
1. Go to your web service settings
2. Add a disk with:
   - Name: `uploads`
   - Mount Path: `/opt/render/project/src/uploads`
   - Size: 10GB (or as needed)

### 7. Deploy and Monitor

1. Render will automatically build and deploy your application
2. Monitor the build logs for any issues
3. Once deployed, your app will be available at: `https://your-service-name.onrender.com`

## Post-Deployment Configuration

### Initialize System Settings
1. Access your deployed application
2. Log in as a site engineer
3. Go to System Settings to configure:
   - Company name
   - Currency (ZMW recommended)
   - Default site information

### Create Initial Data
1. Create sites for your construction projects
2. Add material categories and initial inventory
3. Set up user accounts for storesmen and engineers

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | Auto-generated |
| `SESSION_SECRET` | Flask session encryption key | Yes | Auto-generated |
| `FLASK_ENV` | Flask environment | No | `production` |
| `PORT` | Server port | No | `5000` |
| `PYTHONPATH` | Python module path | No | `/opt/render/project/src` |

## Troubleshooting

### Common Issues

**Build Failures:**
- Check `requirements.txt` for correct package versions
- Ensure all Python files are valid
- Verify no missing imports

**Database Connection:**
- Ensure PostgreSQL service is running
- Check `DATABASE_URL` environment variable
- Verify database credentials

**File Upload Issues:**
- Ensure disk storage is properly mounted
- Check file permissions
- Verify upload directory exists

### Performance Optimization

**Database:**
- Enable connection pooling (already configured)
- Monitor query performance
- Consider upgrading to paid PostgreSQL plan for production

**Application:**
- Monitor memory usage
- Scale workers if needed
- Enable caching for static assets

## Security Considerations

1. **Environment Variables**: Never commit secrets to GitHub
2. **Database**: Use strong passwords and regular backups
3. **File Uploads**: Implement file type validation
4. **HTTPS**: Render provides SSL certificates automatically

## Support and Maintenance

### Monitoring
- Use Render's built-in monitoring
- Set up alerts for downtime
- Monitor database performance

### Updates
- Push code changes to GitHub
- Render will auto-deploy from your main branch
- Test changes in a staging environment first

### Backups
- Regular database backups via Render dashboard
- Export important data periodically
- Maintain local development environment

## Cost Estimation

**Free Tier Includes:**
- Web service with 750 hours/month
- PostgreSQL database with 1GB storage
- 100GB bandwidth
- Basic monitoring

**Paid Plans:**
- Start at $7/month for web services
- Database plans from $7/month
- Additional storage and bandwidth

## Next Steps

1. Deploy using the steps above
2. Configure your company settings
3. Import initial material data
4. Train users on the system
5. Set up regular maintenance schedule

For technical support or questions, refer to the application documentation or contact your development team.