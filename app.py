"""
Main application entry point using Factory Pattern
"""
from app_factory import create_app

# Create app instance using factory pattern
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
