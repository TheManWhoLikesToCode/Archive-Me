from functools import wraps
import logging
import os
import threading
import time

from dotenv import load_dotenv
from flask import Flask, abort, after_this_request, jsonify, make_response, request, send_from_directory
from flask_cors import CORS, cross_origin
from flask_apscheduler import APScheduler


from file_management import clean_up_session_files, delete_session_files, view_in_drive_folder, update_drive_directory, clean_up_docs_files, remove_file_safely, is_file_valid, authorize_drive, get_session_files_path, file_name_from_path
from blackboard_session_manager import BlackboardSessionManager
import config

app = Flask(__name__)
cors = CORS(app)
scheduler = APScheduler()

# Configuration
app.config.from_pyfile(config.__file__)

# Initialize Logging
logging.basicConfig(level=logging.INFO)
# log_level = logging.WARNING
# app.logger.setLevel(log_level)

# Import dot env variables
load_dotenv()


def is_user_logged_in():
    user_session = request.cookies.get('user_session')
    return user_session and bb_session_manager.retrieve_bb_session(user_session)


@scheduler.task('interval', id='clean_up', seconds=600)
def clean_up_and_upload_files_to_google_drive(file_path=None):

    if file_path:
        remove_file_safely(file_path)

    try:
        clean_up_session_files(False)
        delete_session_files()
        update_drive_directory(drive, team_drive_id)
        clean_up_docs_files()
    except Exception as e:
        app.logger.error(f"Error during post-download operations: {e}")


bb_session_manager = BlackboardSessionManager()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_user_logged_in():
            return jsonify({'error': 'Unauthorized access'}), 401
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
@cross_origin()
def index():
    return jsonify({'message': "Welcome to the ArchiveMe's Blackboard Scraper API"})


@app.route('/login', methods=['POST'])
@cross_origin(supports_credentials=True)
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    try:
        bb_session = bb_session_manager.get_bb_session(username)
        bb_session.username = username
        bb_session.password = password

        bb_session.login()
        response = bb_session.get_response()
        if response == 'Login successful.':
            bb_session_manager.put_bb_session(username, bb_session)

            resp = make_response(
                jsonify({'message': 'Logged in successfully'}))
            resp.set_cookie('user_session', bb_session.session_id,
                            max_age=3600, secure=True, httponly=True)
            return resp
        else:
            return jsonify({'error': response}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/logout', methods=['POST'])
@cross_origin(supports_credentials=True)
def logout():
    user_session = request.cookies.get('user_session')
    if user_session:
        # Remove the session from BlackboardSessionManager
        bb_session_manager.delete_bb_session(user_session)

        # Clear the user's session cookie
        resp = make_response(jsonify({'message': 'Logged out successfully'}))
        resp.set_cookie('user_session', '', expires=0)
        return resp
    else:
        return jsonify({'error': 'No active session'}), 400


@app.route('/is_logged_in', methods=['GET'])
@cross_origin(supports_credentials=True)
def is_logged_in():
    user_session = request.cookies.get('user_session')
    if user_session and bb_session_manager.retrieve_bb_session(user_session):
        return jsonify({'logged_in': True}), 200
    else:
        return jsonify({'logged_in': False}), 401


@app.route('/scrape', methods=['GET'])
@cross_origin(supports_credentials=True)
@login_required
def scrape():
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Username is required'}), 400

    try:
        bb_session = bb_session_manager.retrieve_bb_session(username)

        if not bb_session:
            return jsonify({'error': 'Session not found'}), 400

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
@cross_origin(supports_credentials=True)
@login_required
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
            target=clean_up_and_upload_files_to_google_drive, args=(file_path,))
        thread.start()
        return response

    try:
        return send_from_directory(os.getcwd(), file_key, as_attachment=True)
    except Exception as e:
        app.logger.error(f"Error during file download: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/browse/', defaults={'path': None})
@app.route('/browse/<path:path>')
@cross_origin(supports_credentials=True)
@login_required
def list_directory(path):

    if path is None:
        path = team_drive_id
    folders, files = view_in_drive_folder(drive, path, team_drive_id)

    items = folders + files
    if not items:
        file_name = file_name_from_path(drive, path)
        return handle_single_file(path, file_name)

    return jsonify({'folders': folders, 'files': files})


def handle_single_file(file_id, file_name):
    session_files_path = get_session_files_path()
    if not os.path.exists(session_files_path):
        os.makedirs(session_files_path)
    full_path = os.path.join(session_files_path, file_name)

    file = drive.CreateFile({'id': file_id})
    file.GetContentFile(full_path)

    @after_this_request
    def trigger_post_download_operations(response):
        thread = threading.Thread(
            target=clean_up_and_upload_files_to_google_drive, args=(full_path,))
        thread.start()
        return response

    return send_from_directory(session_files_path, file_name, as_attachment=True)


@app.route('/browse')
@login_required
def list_root_directory():
    return list_directory(None)


if __name__ == '__main__':

    drive = authorize_drive()

    if not drive:
        app.logger.error("Error authorizing Google Drive")
        exit(1)

    team_drive_id = '0AFReXfsUal4rUk9PVA'

    scheduler.init_app(app)
    scheduler.start()

    app.run(host='0.0.0.0', port=app.config['PORT'], debug=app.config['DEBUG'])
