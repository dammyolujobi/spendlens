import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# The scope defines what permission you're requesting
# This one is read-only — perfect for a spending tracker
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_gmail_service():
    creds = None

    # token.json stores your credentials after first login
    # so you don't have to log in every time
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If no valid credentials, trigger the login flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "C://Users//USER//Downloads//spendlens//utils//credentials.json", SCOPES
            )
            # Opens a browser tab for you to log in and authorize
            creds = flow.run_local_server(port=0)

        # Save credentials so you only log in once
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    return service