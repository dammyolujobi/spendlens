from fastapi import APIRouter
from fastapi.responses import RedirectResponse, JSONResponse
from utils.auth import get_flow
from datetime import datetime,timedelta
import google.oauth2.id_token
from fastapi import Request
import google.auth.transport.requests
from utils.auth import create_access_token
from router.user import user_collection
from jose import jwt
from slowapi import Limiter
from slowapi.util import get_remote_address
import os
from dotenv import load_dotenv

load_dotenv()


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
oauth_state_store = {}
limiter = Limiter(key_func=get_remote_address)
router = APIRouter(

    tags= ["Setup"]
)

@router.get("/auth/login")
@limiter.limit("5/minute")
def login(request:Request):
    now = datetime.now()

    expired_states = [s for s, data in oauth_state_store.items() 
                      if now - data["created_at"] > timedelta(minutes=10)]
    
    for s in expired_states:
        del(oauth_state_store[s])

    flow = get_flow()
    auth_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent"
    )

    oauth_state_store[state] = {
        "code_verifier": getattr(flow, "code_verifier", None),
        "created_at": datetime.now()
    }

    return RedirectResponse(auth_url)


@router.get("/auth/callback")
@limiter.limit("5/minute")
async def callback(request:Request,code: str, state: str = None,):

    if state not in oauth_state_store:
        return JSONResponse({"Error invalid or missing state"},status_code=400)
    
    state_data = oauth_state_store.pop(state)
   
    if datetime.now() - state_data["created_at"] > timedelta(minutes=10):
        return JSONResponse({"error": "State expired"}, status_code=400)
    
    code_verifier = state_data["code_verifier"]
    flow = get_flow()
    
    if code_verifier:
        flow.fetch_token(code=code, code_verifier=code_verifier)
    else:
        flow.fetch_token(code=code)

    credentials = flow.credentials

    request = google.auth.transport.requests.Request()
    id_info = google.oauth2.id_token.verify_oauth2_token(
        credentials.id_token, request
    )
    

    google_id = id_info["sub"]
    email = id_info["email"]
    name = id_info.get("name","")


    token_data = {
        "token":credentials.token,
        "refresh_token":credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id":credentials.client_id,
        "scopes":list(credentials.scopes or [])
    }


    user_collection.update_one(
        {"google_id":google_id},
        {"$set":{
            "google_id":google_id,
            "email":email,
            "name":name,
            "gmail_token":jwt.encode(token_data,JWT_SECRET_KEY,ALGORITHM)
        }},
        upsert=True
    )

    jwt_token = create_access_token({"sub":google_id,"email":email,"name":email})

    return RedirectResponse(f"http://localhost:3000?token={jwt_token}")


