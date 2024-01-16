import logging
import os
import threading
import time

from dotenv import load_dotenv
from flask import Flask, abort, after_this_request, jsonify, request, send_from_directory
from flask_cors import CORS, cross_origin
from flask_apscheduler import APScheduler

from blackboard_session import BlackboardSession
from file_management import clean_up_session_files, delete_session_files, list_files_in_drive_folder, update_drive_directory, clean_up_docs_files, remove_file_safely, is_file_valid, authorize_drive, get_session_files_path
from blackboard_session_manager import BlackboardSessionManager
import config

app = Flask(__name__)
cors = CORS(app)
scheduler = APScheduler()

# Configuration
app.config.from_pyfile(config.__file__)

# Initialize Logging
logging.basicConfig(level=logging.INFO)

# Import dot env variables
load_dotenv()


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


bb_session_manager = BlackboardSessionManager()


@scheduler.task('interval', id='delete_sessions', seconds=60)
def delete_inactive_bb_sessions(inactivity_threshold_seconds=180):
    current_time = time.time()

    # Collect usernames with inactive sessions for deletion
    usernames_to_delete = []
    for username, session_id in bb_session_manager.user_session_map.items():
        session = bb_session_manager.bb_sessions.get(session_id)
        if session:
            last_activity_time = session.last_activity_time
            inactive_duration = current_time - last_activity_time
            if inactive_duration > inactivity_threshold_seconds:
                usernames_to_delete.append(username)

    # Delete collected usernames' sessions
    for username in usernames_to_delete:
        bb_session_manager.delete_bb_session(username)

    print("Deleting inactive sessions at:", time.time())


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
        bb_session = bb_session_manager.get_bb_session(username)
        bb_session.username = username
        bb_session.password = password

        bb_session.login()
        response = bb_session.get_response()
        if response == 'Login successful.':
            bb_session_manager.put_bb_session(username, bb_session)
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

    if len(items) == 1:
        item = items[0]
        item_type, file_name, file_id = item[1], item[0], item[2]

        if item_type == 'FILE':
            return handle_single_file(file_id, file_name)
        elif item_type == 'FOLDER':
            return jsonify({'error': 'Cannot download a folder.'}), 400

    return jsonify(items)


def handle_single_file(file_id, file_name):
    session_files_path = get_session_files_path()
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
