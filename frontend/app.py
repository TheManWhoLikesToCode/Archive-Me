from flask import Flask, render_template, request, jsonify, send_from_directory, abort
from flask_cors import CORS, cross_origin
import os
import logging
import config

app = Flask(__name__)
CORS(app)

# Configuration
app.config.from_pyfile(config.__file__)

# Initialize Logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
@cross_origin()
def index():
    return render_template('index.html')

@app.route('/demo')
@cross_origin()
def demo():
    return render_template('demo.html')

@app.route('/directory/')
@cross_origin()
def directory():
    return render_template('directory.html')

# Add a login route for demonstration
@app.route('/login', methods=['POST'])
def login():
    # Your login logic here
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=app.config['DEBUG'])
