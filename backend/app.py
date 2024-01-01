from file_management import clean_up_session_files, delete_session_files, list_files_in_drive_folder, update_drive_directory, clean_up_docs_files
from config import chrome_options
import config
import os
import logging
import threading
from flask import Flask, request, jsonify, send_from_directory, abort, after_this_request
from flask_cors import CORS, cross_origin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from blackboard_scraper import log_into_blackboard, download_and_zip_content


def is_file_valid(file_path):
    return os.path.isfile(file_path) and not os.path.islink(file_path)


def remove_file_safely(file_path):
    try:
        if is_file_valid(file_path):
            os.remove(file_path)
    except OSError as error:
        app.logger.error(f"Error removing file: {error}")


def execute_post_download_operations(file_path):
    remove_file_safely(file_path)

    try:
        clean_up_session_files(True)
        delete_session_files()
        update_drive_directory(drive, docs_folder, team_drive_id)
        clean_up_docs_files()
    except Exception as e:
        app.logger.error(f"Error during post-download operations: {e}")


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
docs_folder = 'docs'

class ScraperService:
    def __init__(self):
        self.drivers = {}
        logging.info("ScraperService initialized")

    def initialize_driver(self, username):
        logging.info(f"Initializing driver for {username}")
        if username not in self.drivers:
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                self.drivers[username] = driver
            except Exception as e:
                logging.error(f"Error initializing WebDriver for {username}: {e}")
                raise
        return self.drivers[username]

    def login(self, username, password):
        logging.info(f"Logging in {username}")
        try:
            driver = self.initialize_driver(username)
            return log_into_blackboard(driver, username, password)
        except Exception as e:
            logging.error(f"Error during login for {username}: {e}")
            self.reset(username)
            raise

    def scrape(self, username):
        logging.info(f"Scraping data for {username}")
        driver = self.drivers.get(username)
        if not driver:
            raise Exception("User not logged in or session expired")

        try:
            return download_and_zip_content(driver, username)
        except Exception as e:
            logging.error(f"Error during scraping for {username}: {e}")
            raise
        finally:
            self.reset(username)

    def reset(self, username):
        logging.info(f"Resetting driver for {username}")
        driver = self.drivers.pop(username, None)
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logging.error(f"Error closing WebDriver for {username}: {e}")

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
    Download a file by its file key and then delete it from the server.
    """
    file_path = os.path.join(os.getcwd(), file_key)
    if not is_file_valid(file_path):
        abort(404, description="File not found")

    @after_this_request
    def trigger_post_download_operations(response):
        thread = threading.Thread(
            target=execute_post_download_operations, args=(file_path,))
        thread.start()
        return response

    try:
        return send_from_directory(os.getcwd(), file_key, as_attachment=True)
    except Exception as e:
        app.logger.error(f"Error during file download: {e}")
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
