import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)


def list_folders_in_root(drive):
    file_list = drive.ListFile({'q': "'root' in parents"}).GetList()
    for file in file_list:
        print('title: {}, id: {}'.format(file['title'], file['id']))


def create_folder(drive, folder_name, drive_parent_id='root'):
    folder_metadata = {
        'title': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [{'id': drive_parent_id}]
    }

    folder = drive.CreateFile(folder_metadata)
    folder.Upload()
    return folder['id']


def upload_file_to_folder(drive, folder_id, file_path):
    file = drive.CreateFile(
        {"parents": [{"kind": "drive#fileLink", "id": folder_id}]})
    file.SetContentFile(file_path)
    file.Upload()


def update_drive_directory(drive, local_docs_path, drive_docs_folder_id='root'):
    # Helper function to find a folder in Google Drive
    def find_folder_id(drive, folder_name, parent_id):
        query = f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed=false"
        file_list = drive.ListFile({'q': query}).GetList()
        return file_list[0]['id'] if file_list else None

    # Helper function to list files in a Google Drive folder
    def list_files_in_drive_folder(drive, folder_id):
        query = f"'{folder_id}' in parents and trashed=false"
        file_list = drive.ListFile({'q': query}).GetList()
        return {file['title']: file['id'] for file in file_list}

    # Helper function to upload a folder and its contents to Google Drive
    def upload_folder(drive, local_folder_path, drive_parent_id):
        folder_name = os.path.basename(local_folder_path)
        new_folder_id = create_folder(drive, folder_name, drive_parent_id)

        for filename in os.listdir(local_folder_path):
            filepath = os.path.join(local_folder_path, filename)
            if os.path.isfile(filepath):
                upload_file_to_folder(drive, new_folder_id, filepath)

    # Update the 'docs' folder in Google Drive
    for local_folder_name in os.listdir(local_docs_path):
        local_folder_path = os.path.join(local_docs_path, local_folder_name)

        if os.path.isdir(local_folder_path):
            # Check if this folder exists in Google Drive
            drive_folder_id = find_folder_id(
                drive, local_folder_name, drive_docs_folder_id)

            if drive_folder_id:
                # Folder exists in Drive, check for missing files
                drive_files = list_files_in_drive_folder(
                    drive, drive_folder_id)
                for local_file in os.listdir(local_folder_path):
                    if local_file not in drive_files:
                        local_file_path = os.path.join(
                            local_folder_path, local_file)
                        upload_file_to_folder(
                            drive, drive_folder_id, local_file_path)
            else:
                # Folder does not exist in Drive, upload the entire folder
                upload_folder(drive, local_folder_path, drive_docs_folder_id)


# Example usage
local_docs_path = '/Users/blackhat/Documents/GitHub/Blackboard-Scraper/backend/docs'
update_drive_directory(drive, local_docs_path)
