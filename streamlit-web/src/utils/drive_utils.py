def authenticate_drive(token_file, credentials_file, is_service_account=False):
    from google.oauth2.credentials import Credentials
    from google.oauth2 import service_account
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import os

    creds = None
    # Check if the token file exists
    if is_service_account:
        scopes = ["https://www.googleapis.com/auth/drive"]
        creds = service_account.Credentials.from_service_account_file(token_file, scopes=scopes)
    else:
        creds = Credentials.from_authorized_user_file(token_file)

    # If there are no (valid) credentials available, let the user log in.
    # If the token file does not exist, create it
    if (not creds or not creds.valid) and not is_service_account:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes=["https://www.googleapis.com/auth/drive.file"])
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_file, "w") as token:
            token.write(creds.to_json())
    
    # return service
    from googleapiclient.discovery import build
    service = build("drive", "v3", credentials=creds)
    return service

def upload_file_to_drive(service, file_path, file_name, folder_id):
    from googleapiclient.http import MediaFileUpload

    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype='application/octet-stream')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')


def get_lists_files(service, folder_id):
    results = service.files().list(
        q=f"'{folder_id}' in parents",
        pageSize=10,
        fields="nextPageToken, files(id, name)"
    ).execute()
    items = results.get('files', [])
    return items

def get_next_page(service, page_token):
    results = service.files().list(
        pageToken=page_token,
        pageSize=10,
        fields="nextPageToken, files(id, name)"
    ).execute()
    items = results.get('files', [])
    return items

def create_folder(service, folder_name, parent_id=None):
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        file_metadata['parents'] = [parent_id]

    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')

def delete_file(service, file_id):
    try:
        service.files().delete(fileId=file_id).execute()
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    
def download_file(service, file_id, file_name):
    from googleapiclient.http import MediaIoBaseDownload
    import io
    from pathlib import Path

    request = service.files().get_media(fileId=file_id)
    file_path = f"downloaded-files/{file_name}"
    fh = open(file_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")
    fh.close()
    return file_path

def download_file_from_drive(service, file_id):
    from googleapiclient.http import MediaIoBaseDownload
    from io import BytesIO
    import os

    request = service.files().get_media(fileId=file_id)
    file_path = f"downloaded-files/{file_id}"
    fh = open(file_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")
    fh.close()
    return file_path



