import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)


team_drive_id = '0AFReXfsUal4rUk9PVA'


def is_valid_team_drive_id(drive, team_drive_id):
    try:
        team_drive = drive.auth.service.drives().get(driveId=team_drive_id).execute()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


# Check if the Team Drive ID is valid
valid_team_drive = is_valid_team_drive_id(drive, team_drive_id)
print(f"Team Drive ID is valid: {valid_team_drive}")


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


def list_files_in_drive_folder(drive, folder_id, team_drive_id):
    query = f"'{folder_id}' in parents and trashed=false"
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


def update_drive_directory(drive, local_docs_path, team_drive_id):

    for local_folder_name in os.listdir(local_docs_path):
        local_folder_path = os.path.join(local_docs_path, local_folder_name)

        if os.path.isdir(local_folder_path):
            drive_folder_id = find_folder_id(
                drive, local_folder_name, team_drive_id)

            if drive_folder_id:
                drive_files = list_files_in_drive_folder(
                    drive, drive_folder_id, team_drive_id)
                for local_file in os.listdir(local_folder_path):
                    if local_file not in drive_files:
                        local_file_path = os.path.join(
                            local_folder_path, local_file)
                        upload_file_to_folder(
                            drive, drive_folder_id, local_file_path, team_drive_id)
            else:
                upload_folder(drive, local_folder_path, team_drive_id)


# Example usage
local_docs_path = '/Users/blackhat/Documents/GitHub/Blackboard-Scraper/backend/docs'
# update_drive_directory(drive, local_docs_path, team_drive_id=team_drive_id)

# is_valid_team_drive_id(drive, team_drive_id)

print(list_files_in_drive_folder(drive, team_drive_id, team_drive_id=team_drive_id))
