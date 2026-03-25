from fastapi import FastAPI
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from router import gmail,setup
import uvicorn
from utils.auth import get_flow, save_token, load_token

app = FastAPI()
app.include_router(gmail.router)
app.include_router(setup.router)

app.add_middleware(
   CORSMiddleware,
   allow_origins = ["http://localhost:3000"],
   allow_credentials = True,
   allow_methods = ["*"],
   allow_headers = ["**"]
)
if __name__ == "__main__":
   uvicorn.run(port=8000,reload=True,app="main:app",host="0.0.0.0")