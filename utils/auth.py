import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIALS_FILE = "C://Users//USER//Downloads//spendlens//utils//credentials.json"
TOKEN_FILE = "token.json"
REDIRECT_URI = "http://localhost:8000/auth/callback"


def get_flow():
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    return flow




def save_token(credentials):
    with open(TOKEN_FILE, "w") as f:
        f.write(credentials.to_json())
    print("token.json saved successfully")


def load_token():

    if not os.path.exists(TOKEN_FILE):
        return None

    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # Token is still valid, return it directly
    if creds.valid:
        return creds

    # Token expired but we have a refresh token — refresh it silently
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            save_token(creds)  # Save the refreshed token
            return creds
        except Exception as e:
            print(f"⚠️ Token refresh failed: {e}")
            return None

    return None