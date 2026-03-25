from datetime import datetime, timezone
from fastapi import APIRouter,Depends
from fastapi.responses import JSONResponse
from googleapiclient.discovery import build
import json
from utils.auth import load_token
from utils.email_cleaning import clean_email,extract_email_body,extract_amount,extract_subject_name

router = APIRouter(prefix="/gmail", tags=["Spendings"])



@router.get("/spendings")
def get_message():
    creds = load_token()
    if not creds:
        return JSONResponse(
            {"error": "Not authenticated. Visit http://localhost:8000/auth/login first."},
            status_code=401
        )

    service = build("gmail", "v1", credentials=creds)

    results = service.users().messages().list(
        userId="me",
        q="subject:(debit OR credit OR receipt OR payment OR invoice OR transaction OR transfer)",
        maxResults=20
    ).execute()

    messages = results.get("messages", [])
    if not messages:
        return JSONResponse({"message": "No message related to spending"})

    email_list = []

    for msg in messages:
        detail = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full"
        ).execute()

        headers = {
            h.get("name", "").lower(): h.get("value", "")
            for h in detail.get("payload", {}).get("headers", [])
        }
        date_value = headers.get("date")
        if not date_value:
            internal_ms = detail.get("internalDate")
            if internal_ms:
                date_value = datetime.fromtimestamp(
                    int(internal_ms) / 1000, tz=timezone.utc
                ).isoformat()
            else:
                date_value = "Unknown"

        pre_content = extract_email_body(detail.get("payload", {})) or detail.get("snippet", "Unknown")
        content  = clean_email(pre_content)
        email_list.append({
            "subject": headers.get("subject", "No subject"),
            "from": headers.get("from", "Unknown"),
            "date": date_value,
            "content": content
        })

    return JSONResponse({
        "total_found": len(email_list),
        "emails": email_list
    })

    
@router.get("/get_amount")
def get_amount(email_content: JSONResponse = Depends(get_message)):
    parsed = json.loads(email_content.body)
    emails = parsed["emails"]

    matched = []
    for email in emails:
        amount = extract_amount(email["content"])
        if amount is None or len(amount) < 3 or "not" in email["subject"]:
            continue

        matched.append({
            "from": extract_subject_name(email["from"]),
            "amount": amount,
            "date": email["date"],
            "subject": email["subject"]
        })

    return matched