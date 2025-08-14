# Render Deployment Fix Guide

## Issue: PostgreSQL Connection Error
**Error**: `could not translate host name "dpg-d1r5v5be5dus73eaj13g-a" to address: Name or service not known`

## Root Cause
The render.yaml file is trying to create a new PostgreSQL database, but your deployment needs to use the existing database configuration.

## IMMEDIATE FIX INSTRUCTIONS

### Option 1: Manual Environment Variable Setup (RECOMMENDED)
1. Go to your Render dashboard: https://dashboard.render.com
2. Find your web service: "construction-material-tracker" 
3. Go to Environment tab
4. **DELETE** the current DATABASE_URL variable
5. **ADD** a new Environment Variable:
   - Key: `DATABASE_URL`
   - Value: `postgresql://neondb_owner:npg_p0UDmlM3HRbV@ep-delicate-wave-a51kx1z0.us-east-2.aws.neon.tech/neondb?sslmode=require`
6. Save and redeploy

### Option 2: External Database Connection
1. In Render dashboard, go to your web service
2. Delete the database reference from the Blueprint
3. Set DATABASE_URL manually as above
4. This uses your existing Neon database instead of creating a new one

## Alternative: Create New Render PostgreSQL Database
If you prefer a new database on Render:

1. Go to Render Dashboard
2. Create New > PostgreSQL Database
3. Choose Free plan
4. Name: `construction-tracker-db`
5. Copy the **External Database URL**
6. Update your web service environment variable with this new URL

## Environment Variables Needed
```
DATABASE_URL=postgresql://[your_db_connection_string]
SESSION_SECRET=[auto-generated]
FLASK_ENV=production
PYTHONPATH=/opt/render/project/src
```

## Test After Fix
1. Go to: https://inventory-tracking-y2pg.onrender.com
2. The application should load without database errors
3. You should see the login screen instead of the 500 error

## Why This Happened
The render.yaml blueprint creates infrastructure automatically, but the hostname in the error suggests the PostgreSQL service wasn't properly provisioned or connected.

Your application is properly coded and ready - this is purely a deployment configuration issue.