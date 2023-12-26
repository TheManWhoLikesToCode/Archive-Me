from flask import Flask, render_template, request, jsonify, send_from_directory, abort
from flask_cors import CORS, cross_origin
import os
import logging
import config

app = Flask(__name__)

# Apply CORS to the whole app with specific origin
CORS(app, resources={r"/login": {"origins": "http://127.0.0.1:5002"}})

# Configuration
app.config.from_pyfile(config.__file__)

# Initialize Logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/demo')
def demo():
    return render_template('demo.html')

@app.route('/directory')
def directory():
    return render_template('directory.html')

# Add a login route for demonstration
@app.route('/login', methods=['POST'])
@cross_origin(origin='http://127.0.0.1:5002', headers=['Content-Type', 'Authorization'])
def login():
    # Your login logic here
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=app.config['DEBUG'])
