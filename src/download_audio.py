import os
import random

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def google_drive_service():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file("client.json", SCOPES)
        creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("drive", "v3", credentials=creds)


def get_folder_id(service, folder_name):
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get("files", [])

    if not folders:
        raise Exception(f'"{folder_name}" folder not found!')

    return folders[0]["id"]


def get_files_in_folder(service, folder_id):
    query = f"'{folder_id}' in parents and mimeType contains 'audio'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    return results.get("files", [])


def download_file(service, file_id, filename):
    request = service.files().get_media(fileId=file_id)
    file_path = f"./{filename}"

    with open(file_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Downloading... {int(status.progress() * 100)}%")

    print(f"\nDownloaded: {file_path}")


def main():
    service = google_drive_service()

    # Get "Audio" folder ID
    folder_id = get_folder_id(service, "Audio")

    # Get audio files from folder
    files = get_files_in_folder(service, folder_id)
    if not files:
        print("No audio files found!")
        return

    # Pick a random audio file
    random_file = random.choice(files)
    print(f"Random File Selected: {random_file['name']}")

    # Download it
    download_file(service, random_file["id"], random_file["name"])


if __name__ == "__main__":
    main()
