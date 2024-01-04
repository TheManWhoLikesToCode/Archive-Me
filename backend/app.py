import logging
import os
import threading
from flask import Flask, abort, after_this_request, jsonify, request, send_from_directory, session
from flask_cors import CORS, cross_origin
from blackboard_scraper_R import BlackboardSession
from file_management import clean_up_session_files, delete_session_files, list_files_in_drive_folder, update_drive_directory, clean_up_docs_files
import config
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

app = Flask(__name__)
cors = CORS(app)
app.secret_key = os.urandom(24)

# Configuration
app.config.from_pyfile(config.__file__)

# Initialize Logging
logging.basicConfig(level=logging.INFO)


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


def get_bb_session(username):
    if 'bb_sessions' not in session:
        session['bb_sessions'] = {}

    if username not in session['bb_sessions']:
        session['bb_sessions'][username] = BlackboardSession()

    return session['bb_sessions'][username]

def put_bb_session(username, bb_session):
    session['bb_sessions'][username] = bb_session

@app.route('/login', methods=['POST'])
@cross_origin()
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    try:
        # Retrieve or create a session for the user
        bb_session = get_bb_session(username)
        bb_session.username = username
        bb_session.password = password

        bb_session.login()
        response = bb_session.get_response()
        if response == 'Login successful.':
            put_bb_session(username, bb_session)
            response.headers.add('Access-Control-Allow-Origin', '*')  # Add this line
            return jsonify({'message': 'Logged in successfully'})
        else:
            return jsonify({'error': response}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/scrape', methods=['GET'])

def scrape():
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Username is required'}), 400

    try:
        bb_session = get_bb_session(username)

        file_key = bb_session.scrape() 
        if not bb_session.response:
            file_path = os.path.join(os.getcwd(), file_key)
            if not file_key or not os.path.isfile(file_path):
                abort(404, description="File not found")

            return jsonify({'file_key': file_key})
        else:
            return jsonify({'error': bb_session.response}), 500

    except Exception as e:
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
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    team_drive_id = '0AFReXfsUal4rUk9PVA'
    docs_folder = 'docs'

    app.run(host='0.0.0.0', port=app.config['PORT'], debug=app.config['DEBUG'])
