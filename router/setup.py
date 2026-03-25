from fastapi import APIRouter
from fastapi.responses import RedirectResponse, JSONResponse
from utils.auth import get_flow, save_token, load_token

oauth_state_store = {}
router = APIRouter(
    prefix="/setup",
    tags= ["Setup"]
)
@router.get("/auth/login")
def login():
    flow = get_flow()
    auth_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent"
    )

    oauth_state_store[state] = getattr(flow, "code_verifier", None)

    return RedirectResponse(auth_url)


@router.get("/auth/callback")
def callback(code: str, state: str = None):
    flow = get_flow()

    code_verifier = oauth_state_store.pop(state, None)

    if code_verifier:
        flow.fetch_token(code=code, code_verifier=code_verifier)
    else:
        flow.fetch_token(code=code)

    credentials = flow.credentials
    save_token(credentials)

    return JSONResponse({
        "message": "Login successful! token.json has been created.",
        "next_step": "Visit http://localhost:8000/test to verify Gmail access"
    })



@router.get("/auth/status")
def auth_status():
    creds = load_token()
    if creds:
        return JSONResponse({"status": "authenticated", "valid": creds.valid})
    return JSONResponse({"status": "not authenticated"})