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


def create_folder(drive, folder_name):
    folder_metadata = {'title': folder_name,
                       'mimeType': 'application/vnd.google-apps.folder'}
    folder = drive.CreateFile(folder_metadata)
    folder.Upload()
    return folder['id']


def upload_file_to_folder(drive, folder_id, file_path):
    file = drive.CreateFile(
        {"parents": [{"kind": "drive#fileLink", "id": folder_id}]})
    file.SetContentFile(file_path)
    file.Upload()
