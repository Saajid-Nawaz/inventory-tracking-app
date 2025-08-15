import os
import logging
from app import app

# Configure logging for production
logging.basicConfig(level=logging.INFO)

# Import routes to register them with the app
try:
    import routes_new  # noqa: F401
    logging.info("Routes imported successfully")
except Exception as e:
    logging.error(f"Error importing routes: {e}")
    raise e

# Test route to verify app is working
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'message': 'Construction Material Tracker is running'}, 200

# Debug route for production troubleshooting
@app.route('/debug/routes')
def debug_routes():
    import urllib.parse
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'rule': str(rule.rule)
        })
    return {'routes': routes}, 200

# Comprehensive diagnostic route for Render deployment issues
@app.route('/debug/status')
def debug_status():
    import sys
    from datetime import datetime
    try:
        # Test database connection
        from app import db
        db.create_all()
        db_status = "Connected"
        
        # Test environment variables
        env_vars = {
            'DATABASE_URL': 'Set' if os.environ.get('DATABASE_URL') else 'Missing',
            'SESSION_SECRET': 'Set' if os.environ.get('SESSION_SECRET') else 'Missing',
            'PORT': os.environ.get('PORT', 'Not Set'),
            'FLASK_ENV': os.environ.get('FLASK_ENV', 'Not Set')
        }
        
        return {
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'python_version': sys.version,
            'database_status': db_status,
            'environment_variables': env_vars,
            'app_config': {
                'secret_key_set': bool(app.secret_key),
                'database_uri_set': bool(app.config.get('SQLALCHEMY_DATABASE_URI'))
            }
        }, 200
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logging.info(f"Starting application on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
