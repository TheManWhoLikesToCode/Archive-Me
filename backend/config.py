# config.py
from selenium.webdriver.chrome.options import Options

# Flask configuration
DEBUG = True  # Set to False in production
PORT = 5001  # Port number for the Flask server

# Selenium configuration
CHROME_DRIVER_PATH = 'support/chromedriver_mac64/chromedriver'  # Path to the ChromeDriver executable

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
chrome_options.add_argument("--disable-images")
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)

# Application specific configurations
# Add other configurations as needed, such as database URIs, API keys, etc.
# Example: DATABASE_URI = 'mysql+pymysql://user:password@localhost/dbname'

# Security configurations
# It's advisable to use environment variables for sensitive data
# Example: SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-default-secret'
