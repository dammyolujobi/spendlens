from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router import gmail,setup,user
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()
ORIGIN = os.getenv("ORIGIN")
app = FastAPI()
app.include_router(gmail.router)
app.include_router(setup.router)
app.include_router(user.router)


app.add_middleware(
   CORSMiddleware,
   allow_origins = [ORIGIN],
   allow_credentials = True,
   allow_methods = ["GET","POST"],
   allow_headers = ["Content-Type","Authorization"]
)
if __name__ == "__main__":
   uvicorn.run(port=8000,reload=False,app="main:app",host="0.0.0.0")