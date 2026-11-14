import os

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes required for Google Drive access
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def generate_token():
    creds = None

    # Check if token.json already exists
    if os.path.exists("token.json"):
        print("Token already exists.")
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    else:
        # Run OAuth flow to get new token
        flow = InstalledAppFlow.from_client_secrets_file("client.json", SCOPES)
        creds = flow.run_local_server(port=0)

        # Save the token for future use
        with open("token.json", "w") as token_file:
            token_file.write(creds.to_json())

        print("Token generated and saved to token.json")

    return creds


if __name__ == "__main__":
    generate_token()
