from flask import Flask, render_template, request, jsonify, send_file
from selenium import webdriver
from scraper import download_and_zip_content
import os

app = Flask(__name__)

# Temporary storage for file path
file_storage = {}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/demo')
def demo():
    return render_template('demo.html')


@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
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


@app.route('/download/<file_key>')
def downloadFile(file_key):
    # Retrieve the file path from storage
    file_path = file_storage.get(file_key)

    # Check if file exists
    if file_path and os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404


if __name__ == '__main__':
    app.run(debug=True)
