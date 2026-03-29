import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from jose import jwt
load_dotenv()

# Environment detection
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # Default to development

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.readonly"
]

# Different redirect URIs for each environment
REDIRECT_URI = f"{os.getenv("REDIRECT_URI")}/auth/callback"

CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE", "utils/credentials.json")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")
TOKEN_FILE = "token.json"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60
REFRESH_TOKEN_EXPIRE_MINUTES = 24 * 60 * 7
ALGORITHM = os.getenv("ALGORITHM")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")

def get_flow():
    if GOOGLE_CREDENTIALS_JSON:
        # Production: load from environment variable
        credentials_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
        flow = Flow.from_client_config(
            credentials_dict,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
    else:
        # Development: load from file
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
    return flow


def save_token(credentials):
    with open(TOKEN_FILE, "w") as f:
        f.write(credentials.to_json())
   


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
            print(f"Token refresh failed: {e}")
            return None

    return None


def create_access_token(subject: dict, expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.now(timezone.utc) + expires_delta
    else:
        expires_delta = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {**subject, "exp": expires_delta}
    encode_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encode_jwt

def create_refresh_token(subject:dict, expires_delta:int = None)-> str:
    if expires_delta is not None:
        expires_delta = datetime.now(timezone.utc) + expires_delta
    else:
        expires_delta = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    
    to_encode = ({"exp": expires_delta,"sub":str(subject)})
    encode_jwt = jwt.encode(to_encode,JWT_REFRESH_SECRET_KEY,ALGORITHM)
    
    return encode_jwt
