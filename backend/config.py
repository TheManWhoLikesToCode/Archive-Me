# config.py
import os
from dotenv import load_dotenv
import sys
# Flask configuration
load_dotenv()

env = os.environ.get('ENVIRONMENT')

if env == 'dev':
    PORT = 5003
    DEBUG = False
elif env == 'prod':
    PORT = 5001
    DEBUG = False
else:
    print("Environment not specified. Please provide a valid environment.")
    sys.exit(1)
