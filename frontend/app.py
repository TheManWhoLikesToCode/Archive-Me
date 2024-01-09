from flask import Flask, render_template, request, jsonify, send_from_directory, abort
from flask_cors import CORS, cross_origin
from config import get_config
import logging
import config

app = Flask(__name__)
CORS(app)

# Configuration
config = get_config()
app.config.from_object(config)

# Initialize Logging
logging.basicConfig(level=logging.INFO)


@app.route('/')
@cross_origin()
def index():
    return render_template('index.html', api_url=app.config['API_URL'])


@app.route('/demo')
@cross_origin()
def demo():
    return render_template('demo.html', api_url=app.config['API_URL'])


@app.route('/directory/')
@cross_origin()
def directory():
    return render_template('directory.html', api_url=app.config['API_URL'])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=app.config['DEBUG'])
