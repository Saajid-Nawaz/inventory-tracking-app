from app import app

# Import routes to register them with the app
try:
    import routes_new  # noqa: F401
    print("Routes loaded successfully")
except Exception as e:
    print(f"Error loading routes: {e}")
    import traceback
    traceback.print_exc()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
