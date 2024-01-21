from flask import Flask, render_template
from flask_cors import CORS, cross_origin
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


@app.route('/TOS')
@cross_origin()
def TOS():
    return render_template('TOS.html')


@app.route('/login')
@cross_origin()
def login():
    return render_template('login.html')


@app.route('/logout')
@cross_origin()
def logout():
    return render_template('logout.html')


@app.route('/userpage')
@cross_origin()
def userPage():
    return render_template('userPage.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=app.config['DEBUG'])
