import os
import logging
from app import app

# Configure logging for production
logging.basicConfig(level=logging.INFO)

# Import routes to register them with the app
import routes_new  # noqa: F401

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

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    logging.info(f"Starting application on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
