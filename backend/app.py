import os
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory, abort
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from blackboard_scraper import log_into_blackboard, download_and_zip_content
from file_management import clean_up_files
from flask_cors import CORS, cross_origin 
from config import chrome_options
import config

app = Flask(__name__)
cors = CORS(app)

# Configuration
app.config.from_pyfile(config.__file__)

# Initialize Logging
logging.basicConfig(level=logging.INFO)

class ScraperService:
    def __init__(self):
        self.driver = None
        self.current_username = None

    def initialize_driver(self):
        if not self.driver:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)


    def login(self, username, password):
        self.initialize_driver()
        return log_into_blackboard(self.driver, username, password)

    def scrape(self):
        return download_and_zip_content(self.driver, self.current_username)

    def reset(self):
        if self.driver:
            self.driver.quit()
        self.driver = None
        self.current_username = None


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
        scraper_service.current_username = username
        result = scraper_service.login(username, password)
        if isinstance(result, str):
            return jsonify({'error': result}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return "Logged in successfully"


@app.route('/scrape', methods=['GET'])
def scrape():
    if not scraper_service.current_username:
        return jsonify({'error': 'User not logged in'}), 401

    try:
        file_key = scraper_service.scrape()
        scraper_service.reset()

        file_path = os.path.join(os.getcwd(), file_key)
        if not file_key or not os.path.isfile(file_path):
            abort(404, description="File not found")

        return jsonify({'file_key': file_key})
    except Exception as e:
        scraper_service.reset()
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


@app.route('/directory/<path:path>')
@cross_origin()
def list_directory(path):
    print("Requested Path:", path)  # Debugging print statement

    base_dir = '/Users/blackhat/Documents/GitHub/Blackboard-Scraper/docs'
    abs_path = os.path.join(base_dir, path)

    if os.path.exists(abs_path):
        if os.path.isdir(abs_path):
            items = os.listdir(abs_path)
            return render_template('directory.html', items=items, path=path)
        else:
            # Handle file download if the path is a file
            return send_from_directory(base_dir, path, as_attachment=True)
    else:
        return "Path does not exist", 404

@app.route('/directory/')
@app.route('/directory')
def docs_root():
    return list_directory('')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=app.config['DEBUG'])
