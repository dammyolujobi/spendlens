import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
from jose import jwt
load_dotenv()

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.readonly"
]
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE")
REDIRECT_URI = "http://localhost:8000/auth/callback"
ACCESS_TOKEN_EXPIRE_MINUTES =24 * 60
REFRESH_TOKEN_EXPIRE_MINUTES = 24 * 60
ALGORITHM = os.getenv("ALGORITHM")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")

def get_flow():
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    return flow


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
