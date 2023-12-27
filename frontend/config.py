# config.py

# Flask configuration
DEBUG = True  # Set to False in production
PORT = 5002  # Port number for the Flask server

# CORS Configurations
CORS_HEADERS = 'Content-Type'

# Security configurations
# It's advisable to use environment variables for sensitive data
# Example: SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-default-secret'
