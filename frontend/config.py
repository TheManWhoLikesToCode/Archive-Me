# config.py
import os
from dotenv import load_dotenv
import sys

# Flask configuration
load_dotenv()

env = os.environ.get('ENVIRONMENT')

if env == 'dev':
    PORT = 5004
    DEBUG = True
elif env == 'prod':
    PORT = 5002
    DEBUG = False
else:
    print("Environment not specified. Please provide a valid environment.")
    sys.exit(1)

# CORS Configurations
CORS_HEADERS = 'Content-Type'
