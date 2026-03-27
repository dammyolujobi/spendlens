from fastapi import APIRouter,Depends,status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from pymongo import MongoClient
import os
from fastapi.security import HTTPBearer
from dotenv import load_dotenv
from jose import jwt,JWTError



load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
client = MongoClient(CONNECTION_STRING)

router = APIRouter(
    prefix = "/user",
    tags=["User"]
)

def get_db():
    return client["spend_lens"]

db_name = get_db()

user_collection = db_name["user"]

@router.get("/get_current_user")
async def get_current_user(token: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM]) 
        google_id = payload.get("sub")
        if not google_id:
            raise credentials_exception
        return google_id
    except JWTError:
        raise credentials_exception