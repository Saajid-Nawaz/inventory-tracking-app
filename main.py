from app import app
import routes_new  # noqa: F401
from routes_api import api_bp

# Register API blueprint
app.register_blueprint(api_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
