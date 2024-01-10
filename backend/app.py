import logging
import os
import threading
import time
import uuid

from dotenv import load_dotenv
from flask import Flask, abort, after_this_request, jsonify, request, send_from_directory
from flask_cors import CORS, cross_origin
from flask_apscheduler import APScheduler
import yaml

from blackboard_scraper import BlackboardSession
from file_management import clean_up_session_files, delete_session_files, list_files_in_drive_folder, update_drive_directory, clean_up_docs_files
import config

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

app = Flask(__name__)
cors = CORS(app)
scheduler = APScheduler()

# Configuration
app.config.from_pyfile(config.__file__)

# Initialize Logging
logging.basicConfig(level=logging.INFO)

# Import dot env variables
load_dotenv()


def is_file_valid(file_path):
    return os.path.isfile(file_path) and not os.path.islink(file_path)


def remove_file_safely(file_path):
    try:
        if is_file_valid(file_path):
            os.remove(file_path)
    except OSError as error:
        app.logger.error(f"Error removing file: {error}")


@scheduler.task('interval', id='clean_up', seconds=600)
def clean_up_and_upload_files_to_google_drive(file_path=None):

    if file_path:
        remove_file_safely(file_path)

    try:
        clean_up_session_files(True)
        delete_session_files()
        update_drive_directory(drive, team_drive_id)
        clean_up_docs_files()
    except Exception as e:
        app.logger.error(f"Error during post-download operations: {e}")


def authorize_drive():
    with open('settings.yaml', 'r') as file:
        settings = yaml.safe_load(file)

    settings['client_config']['client_id'] = os.environ.get('GOOGLE_CLIENT_ID')
    settings['client_config']['client_secret'] = os.environ.get(
        'GOOGLE_CLIENT_SECRET')

    gauth = GoogleAuth(settings=settings)

    if os.path.isfile("credentials.json"):
        gauth.LoadCredentialsFile("credentials.json")
    else:
        gauth.LocalWebserverAuth()
        gauth.SaveCredentialsFile("credentials.json")

    if gauth.access_token_expired:
        gauth.Refresh()
        gauth.SaveCredentialsFile("credentials.json")
    
    drive = GoogleDrive(gauth)
    return drive


bb_sessions = {}


def get_bb_session(username):
    if 'bb_sessions' not in bb_sessions:
        bb_sessions['bb_sessions'] = {}

    if username not in bb_sessions['bb_sessions']:
        session_id = str(uuid.uuid4())  # Generate a unique session ID
        bb_sessions['bb_sessions'][username] = session_id
        # Store the session object
        bb_sessions[session_id] = BlackboardSession()

    return bb_sessions[bb_sessions['bb_sessions'][username]]


def put_bb_session(username, bb_session):
    session_id = bb_sessions['bb_sessions'].get(username)
    if session_id:
        bb_sessions[session_id] = bb_session


def retrieve_bb_session(username):
    if 'bb_sessions' not in bb_sessions:
        bb_sessions['bb_sessions'] = {}

    session_id = bb_sessions['bb_sessions'].get(username)
    if session_id:
        return bb_sessions.get(session_id)

    return None


def delete_bb_session(username):
    session_id = bb_sessions['bb_sessions'].get(username)
    if session_id:
        session_to_delete = bb_sessions.pop(session_id, None)
        if session_to_delete:
            del bb_sessions['bb_sessions'][username]


@scheduler.task('interval', id='delete_sessions', seconds=60)
def delete_inactive_bb_sessions(inactivity_threshold_seconds=180):
    current_time = time.time()

    # Check if 'bb_sessions' key exists
    if 'bb_sessions' not in bb_sessions:
        return  # No sessions exist yet

    # Collect usernames with inactive sessions for deletion
    usernames_to_delete = []
    for username, session_id in bb_sessions['bb_sessions'].items():
        session = bb_sessions.get(session_id)
        if session:
            last_activity_time = session.last_activity_time
            inactive_duration = current_time - last_activity_time
            if inactive_duration > inactivity_threshold_seconds:
                usernames_to_delete.append(username)

    # Delete collected usernames' sessions
    for username in usernames_to_delete:
        delete_bb_session(username)

    print("Deleting inactive sessions at:", time.time())

    session_id = bb_sessions['bb_sessions'].get(username)
    return bb_sessions.get(session_id)


@app.route('/')
@cross_origin()
def index():
    return jsonify({'message': "Welcome to the ArchiveMe's Blackboard Scraper API"})


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
        bb_session = retrieve_bb_session(username)

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
@cross_origin()
def list_directory(path):
    print("Requested Path:", path)

    if path is None:
        path = team_drive_id
    items = list_files_in_drive_folder(drive, path, team_drive_id)

    # Check if there's only one file returned
    if len(items) == 1 and items[0][3] == 'FILE':
        # Assuming 'file_id' and 'file_name' are available based on the user selection
        file_id = items[0][2]
        file_name = items[0][0]

        # Update the session_files_path based on the current directory and create if it doesn't exist
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if os.path.basename(current_dir) != 'backend':
            session_files_path = os.path.join(
                current_dir, 'backend', 'Session Files')
        else:
            session_files_path = os.path.join(current_dir, 'Session Files')

        # Check if the Session Files directory exists, if not, create it
        if not os.path.exists(session_files_path):
            os.makedirs(session_files_path)
        full_path = os.path.join(session_files_path, file_name)

        file = drive.CreateFile({'id': file_id})
        print('Downloading file %s from Google Drive' % file_name)
        file.GetContentFile(full_path)

        @after_this_request
        def trigger_post_download_operations(response):
            thread = threading.Thread(
                target=clean_up_and_upload_files_to_google_drive, args=(full_path,))
            thread.start()
            return response

        return send_from_directory(session_files_path, file_name, as_attachment=True)

    return jsonify(items)


@app.route('/browse')
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
