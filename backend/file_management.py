from googleapiclient.errors import HttpError
import logging
import os
import shutil
from flask import app
import yaml
from pdf_compressor import compress
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


def compress_pdfs(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.pdf'):
                file_path = os.path.join(root, file)
                compressed_file_path = file_path[:-4] + '-c.pdf'
                compress(file_path, compressed_file_path, power=4)
                os.remove(file_path)


def clean_up_session_files(compress_files):
    current_dir = os.getcwd()

    # Determine the session_files_path based on the current directory
    if os.path.basename(current_dir) != 'backend':
        session_files_path = os.path.join(
            current_dir, 'backend', 'Session Files')
        docs_path = os.path.join(current_dir, 'backend', 'docs')
    else:
        session_files_path = os.path.join(current_dir, 'Session Files')
        docs_path = os.path.join(current_dir, 'docs')

    if not os.path.exists(session_files_path):
        return

    if compress_files:
        # Compress PDFs within the session files path
        compress_pdfs(session_files_path)

    for item in os.listdir(session_files_path):
        source_item_path = os.path.join(session_files_path, item)
        dest_item_path = os.path.join(docs_path, item)

        if os.path.isdir(source_item_path):
            if not os.path.exists(dest_item_path):
                shutil.move(source_item_path, dest_item_path)
            else:
                for sub_item in os.listdir(source_item_path):
                    source_sub_item = os.path.join(source_item_path, sub_item)
                    dest_sub_item = os.path.join(dest_item_path, sub_item)

                    if os.path.isdir(source_sub_item):
                        if not os.path.exists(dest_sub_item):
                            shutil.move(source_sub_item, dest_sub_item)
                        else:
                            shutil.rmtree(dest_sub_item)
                            shutil.move(source_sub_item, dest_sub_item)
                    elif os.path.isfile(source_sub_item) and not os.path.exists(dest_sub_item):
                        shutil.move(source_sub_item, dest_sub_item)

                # If the source directory is now empty, remove it
                if not os.listdir(source_item_path):
                    shutil.rmtree(source_item_path)

            print(f"Processed {item}")

    print("Folders merged into 'docs' successfully.")


def delete_session_files():
    current_dir = os.getcwd()

    # Check if the current directory ends with 'backend'. If not, append 'backend' to the path
    if os.path.basename(current_dir) != 'backend':
        session_files_path = os.path.join(
            current_dir, 'backend', 'Session Files')
    else:
        session_files_path = os.path.join(current_dir, 'Session Files')

    # Check if the session_files_path exists
    if not os.path.exists(session_files_path):
        return

    shutil.rmtree(session_files_path)
    print("Session files deleted successfully.")


def clean_up_docs_files():

    current_dir = os.getcwd()

    # Check if the current directory ends with 'backend'. If not, append 'backend' to the path
    if os.path.basename(current_dir) != 'backend':
        docs_file_path = os.path.join(current_dir, 'backend', 'docs')
    else:
        docs_file_path = os.path.join(current_dir, 'docs')

    # Check if the docs_file_path exists
    if not os.path.exists(docs_file_path):
        return
    shutil.rmtree(docs_file_path)
    print("Docs files deleted successfully.")


def is_valid_team_drive_id(drive, team_drive_id):
    try:
        team_drive = drive.auth.service.drives().get(driveId=team_drive_id).execute()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def create_folder(drive, folder_name, parent_id, team_drive_id):
    folder_metadata = {
        'title': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [{'id': parent_id if parent_id else 'root'}]
    }
    if team_drive_id:
        folder_metadata['teamDriveId'] = team_drive_id
        folder_metadata['supportsTeamDrives'] = True

    folder = drive.CreateFile(folder_metadata)
    folder.Upload()
    return folder['id']


def upload_file_to_folder(drive, folder_id, file_path, team_drive_id=None):
    file_metadata = {
        "parents": [{"kind": "drive#fileLink", "id": folder_id}]
    }
    if team_drive_id:
        file_metadata['teamDriveId'] = team_drive_id
        file_metadata['supportsTeamDrives'] = True

    file = drive.CreateFile(file_metadata)
    file.SetContentFile(file_path)
    file.Upload()


def find_folder_id(drive, folder_name, team_drive_id):
    query = f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if team_drive_id:
        query += f" and '{team_drive_id}' in parents"
        file_list = drive.ListFile({'q': query, 'supportsTeamDrives': True, 'includeTeamDriveItems': True,
                                   'corpora': 'teamDrive', 'teamDriveId': team_drive_id}).GetList()
    else:
        query += " and 'root' in parents"
        file_list = drive.ListFile({'q': query}).GetList()
    return file_list[0]['id'] if file_list else None


def view_in_drive_folder(drive, team_drive_id):
    query = f"'{team_drive_id}' in parents and trashed=false"
    file_list = drive.ListFile(
        {'q': query, 'supportsTeamDrives': True, 'includeTeamDriveItems': True}).GetList()
    return {file['title']: file['id'] for file in file_list}


def upload_folder(drive, local_folder_path, team_drive_id):
    folder_name = os.path.basename(local_folder_path)
    # The parent ID for a folder in the root of the Team Drive is 'root'
    new_folder_id = create_folder(
        drive, folder_name, team_drive_id, team_drive_id)

    for filename in os.listdir(local_folder_path):
        filepath = os.path.join(local_folder_path, filename)
        if os.path.isfile(filepath):
            upload_file_to_folder(drive, new_folder_id,
                                  filepath, team_drive_id)

def file_name_from_path(drive, drive_id):
    file = drive.CreateFile({'id': drive_id})
    return file['title']

def update_drive_directory(drive, team_drive_id):

    current_dir = os.getcwd()

   # Check if the current directory ends with 'backend'. If not, append 'backend' to the path
    if os.path.basename(current_dir) != 'backend':
        docs_file_path = os.path.join(current_dir, 'backend', 'docs')
    else:
        docs_file_path = os.path.join(current_dir, 'docs')

    if not os.path.exists(docs_file_path):
        return

    for local_folder_name in os.listdir(docs_file_path):
        local_folder_path = os.path.join(docs_file_path, local_folder_name)

        if os.path.isdir(local_folder_path):
            drive_folder_id = find_folder_id(
                drive, local_folder_name, team_drive_id)

            if drive_folder_id:
                # Modified to get only the names of the files in the Drive folder
                drive_files = [file_info[0] for file_info in view_in_drive_folder(
                    drive, drive_folder_id, team_drive_id)]

                for local_file in os.listdir(local_folder_path):
                    if local_file not in drive_files:
                        local_file_path = os.path.join(
                            local_folder_path, local_file)
                        print(
                            f"Uploading file: {local_file_path} to folder: {local_folder_name}")
                        upload_file_to_folder(
                            drive, drive_folder_id, local_file_path, team_drive_id)
            else:
                print(f"Uploading folder: {local_folder_path}")
                upload_folder(drive, local_folder_path, team_drive_id)


def view_in_drive_folder(drive, folder_id, team_drive_id):
    try:
        query = f"'{folder_id}' in parents and trashed=false"
        params = {'q': query}

        if team_drive_id:
            params.update({'supportsTeamDrives': True, 'includeTeamDriveItems': True,
                           'corpora': 'teamDrive', 'teamDriveId': team_drive_id})

        directory = drive.ListFile(params).GetList()

        folders, files = [], []

        for instance in directory:
            item = [instance['title'], instance['mimeType'], instance['id']]
            (folders if instance['mimeType'] ==
             'application/vnd.google-apps.folder' else files).append(item)

        return sorted(folders, key=lambda x: x[0]), sorted(files, key=lambda x: x[0])

    except HttpError as http_error:
        logging.error(f"HTTP error in view_in_drive_folder: {http_error}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error in view_in_drive_folder: {e}")
        raise


def is_file_valid(file_path):
    normalized_path = os.path.normpath(file_path)
    return os.path.isfile(normalized_path) and not os.path.islink(normalized_path)


def remove_file_safely(file_path):
    try:
        if is_file_valid(file_path):
            os.remove(file_path)
    except OSError as error:
        app.logger.error(f"Error removing file: {error}")


def authorize_drive():
    current_directory = os.getcwd()

    if 'backend' in current_directory:
        settings_path = 'settings.yaml'
    elif 'Archive-Me' in current_directory:
        settings_path = 'backend/settings.yaml'
    else:
        raise Exception("Unable to locate settings file.")

    with open(settings_path, 'r') as file:
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


def get_session_files_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(current_dir) != 'backend':
        return os.path.join(current_dir, 'backend', 'Session Files')
    else:
        return os.path.join(current_dir, 'Session Files')