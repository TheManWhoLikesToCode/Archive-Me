from flask import Flask, render_template, request, jsonify, send_from_directory, abort
from selenium import webdriver
from scraper import download_and_zip_content
import os

app = Flask(__name__)

# Temporary storage for file path
file_storage = {}


@app.route('/')
def index():
    print('Received request: GET /')
    return render_template('index.html')


@app.route('/demo')
def demo():
    print('Received request: GET /demo')
    return render_template('demo.html')


@app.route('/scrape', methods=['POST'])
def scrape():
    print('Received request: POST /scrape')
    data = request.json
    print('Request contents:', data)  # Print the request contents
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    try:
        driver = webdriver.Chrome()
        result = download_and_zip_content(driver, username, password)
        driver.quit()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    file_key = username  # Assuming username is unique for each session
    file_storage[file_key] = result

    return jsonify({'file_key': file_key})  # Send back the unique key


@app.route('/download/<file_key>', methods=['GET'])
def download_file(file_key):
    print(f'Received request: GET /download/{file_key}')
    current_directory = os.path.dirname(os.path.realpath(__file__)) 
    file_path = os.path.join(current_directory, file_key)  
    
    if not os.path.isfile(file_path):
        abort(404, description="File not found")  # Handle the case where the file doesn't exist

    return send_from_directory(current_directory, file_key, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
