from flask import Flask, render_template, request, jsonify, send_from_directory, abort
from selenium import webdriver
from scraper import download_and_zip_content, log_into_blackboard, clean_up_files
import os

app = Flask(__name__)

# Temporary storage for file path
file_storage = {}

driver = None  # Initialize the driver variable
current_username = None  # Initialize a global variable for username


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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return "Logged in successfully"


@app.route('/scrape', methods=['GET'])
def scrape():
    global driver, current_username  # Use the global driver and username variables
    print('Received request: GET /scrape')

    if driver is None or current_username is None:
        return jsonify({'error': 'User not logged in'}), 401

    try:
        result = download_and_zip_content(driver)
        driver.quit()
        driver = None  # Reset the driver after use
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    file_key = current_username  # Use the stored username as the unique identifier
    file_storage[file_key] = result
    current_username = None  # Reset the username after scraping

    return jsonify({'file_key': file_key})  # Send back the unique key


@app.route('/download/<file_key>', methods=['GET'])
def download_file(file_key):
    print(f'Received request: GET /download/{file_key}')
    current_directory = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(current_directory, file_key)

    if not os.path.isfile(file_path):
        # Handle the case where the file doesn't exist
        abort(404, description="File not found")
    
    return send_from_directory(current_directory, file_key, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
