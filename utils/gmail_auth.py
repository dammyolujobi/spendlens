
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def get_gmail_service(user:dict):
    token_data  = user["gmail_token"]

    creds = Credentials(
        token=token_data["token"],
        refresh_token=token_data["refresh_token"],
        token_uri=token_data["token_uri"],
        client_id=token_data["client_id"],
        client_secret=token_data["client_secret"],
        scopes=token_data["scopes"],
    )

    return build("gmail","v1",credentials=creds)