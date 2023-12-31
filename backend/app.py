import os
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory, abort
from flask_cors import CORS, cross_origin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from blackboard_scraper import log_into_blackboard, download_and_zip_content
from file_management import find_folder_id, list_files_in_drive_folder
import config
from config import chrome_options

app = Flask(__name__)
cors = CORS(app)

# Configuration
app.config.from_pyfile(config.__file__)

print("Starting Flask server on port", app.config['PORT'])

# Initialize Logging
logging.basicConfig(level=logging.INFO)

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

team_drive_id = '0AFReXfsUal4rUk9PVA'


class ScraperService:
    def __init__(self):
        self.drivers = {}  # Dictionary to hold drivers for each user

    def initialize_driver(self, username):
        if username not in self.drivers:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            self.drivers[username] = driver
        return self.drivers[username]

    def login(self, username, password):
        driver = self.initialize_driver(username)
        return log_into_blackboard(driver, username, password)

    def scrape(self, username):
        driver = self.drivers.get(username)
        if driver:
            return download_and_zip_content(driver, username)
        else:
            raise Exception("User not logged in or session expired")

    def reset(self, username):
        driver = self.drivers.pop(username, None)
        if driver:
            driver.quit()


scraper_service = ScraperService()


@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    try:
        result = scraper_service.login(username, password)
        if isinstance(result, str):
            return jsonify({'error': result}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Logged in successfully'})



@app.route('/scrape', methods=['GET'])
def scrape():
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Username is required'}), 400

    try:
        file_key = scraper_service.scrape(username)
        scraper_service.reset(username)

        file_path = os.path.join(os.getcwd(), file_key)
        if not file_key or not os.path.isfile(file_path):
            abort(404, description="File not found")

        return jsonify({'file_key': file_key})
    except Exception as e:
        scraper_service.reset(username)
        return jsonify({'error': str(e)}), 500


@app.route('/download/<file_key>', methods=['GET'])
@cross_origin()
def download(file_key):
    """
    Download a file by its file key.
    """
    try:
        file_path = os.path.join(os.getcwd(), file_key)
        if not os.path.isfile(file_path):
            abort(404, description="File not found")

        return send_from_directory(os.getcwd(), file_key, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/browse/', defaults={'path': None})
@app.route('/browse/<path:path>')
@cross_origin()
def list_directory(path):
    print("Requested Path:", path)  
    
    if path is None:
        path = team_drive_id
    items = list_files_in_drive_folder(drive, path, team_drive_id)

    return jsonify(items)

@app.route('/browse')
def list_root_directory():
    return list_directory(None)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=app.config['DEBUG'])
