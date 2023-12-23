from flask import Flask, render_template, request, jsonify, send_from_directory, abort, current_app
from selenium import webdriver
from scraper import download_and_zip_content, log_into_blackboard, clean_up_files
import os

app = Flask(__name__)

# Temporary storage for file path
file_storage = {}

driver = None  # Initialize the driver variable
current_username = None  # Initialize a global variable for username
file_key = None  # Declare file_key as a global variable

@app.route('/')
def index():
    print('Received request: GET /')
    return render_template('index.html')

@app.route('/demo')
def demo():
    print('Received request: GET /demo')
    return render_template('demo.html')

@app.route('/login', methods=['POST'])
def login():
    global driver, current_username  # Use the global driver and username variables
    print('Received request: POST /login')
    data = request.json
    print('Request contents:', data)  # Print the request contents
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    try:
        if driver is None:  # Check if the driver is not already initialized
            driver = webdriver.Chrome()
        logged_in_driver = log_into_blackboard(driver, username, password)
        if isinstance(logged_in_driver, str):
            return jsonify({'error': logged_in_driver}), 401
        current_username = username  # Store the username after successful login
        print(current_username)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return "Logged in successfully"

@app.route('/scrape', methods=['GET'])
def scrape():

    global driver, current_username, file_key  # Use the global driver and username variables
    print('Received request: GET /scrape')

    # Check if the user is logged in
    if driver is None or current_username is None:
        return jsonify({'error': 'User not logged in'}), 401

    try:
        # Perform scraping and get the file key
        file_key = download_and_zip_content(driver, current_username)
        driver.quit()
        driver = None  # Reset the driver after use
        current_username = None  # Reset the username after scraping

        # Prepare for file download
        current_directory = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(current_directory, file_key)

        if not file_key or not os.path.isfile(file_path):
            abort(404, description="File not found")

        return send_from_directory(
            current_directory, file_key, as_attachment=True)

    except Exception as e:
        if driver:
            driver.quit()
            driver = None
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['GET'])
def download():
    global file_key
    if not file_key:
        abort(404, description="File not found")

    uploads = os.path.dirname(os.path.realpath(__file__))
    return send_from_directory(uploads, file_key, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
