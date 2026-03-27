from datetime import datetime, timezone
from fastapi import APIRouter,Depends
from fastapi.responses import JSONResponse
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import json
from router.user import get_current_user, user_collection
from utils.email_cleaning import clean_email,extract_email_body,extract_amount,extract_subject_name
import os
from jose import jwt
from dotenv import load_dotenv

load_dotenv()


router = APIRouter(prefix="/gmail", tags=["Spendings"])

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

@router.get("/spendings")
def get_message(user:str = Depends(get_current_user)):
    try:

        user_doc = user_collection.find_one({"google_id": user})
        if not user_doc or "gmail_token" not in user_doc:
            return JSONResponse(
                {"error": "Gmail credentials not found. Please login with Google first."},
                status_code=401
            )
        
        # Reconstruct credentials from stored token data
        token_data = user_doc["gmail_token"]
        token_data = jwt.decode(token_data, SECRET_KEY, algorithms=[ALGORITHM])
        token_data["client_secret"] = os.getenv("GOOGLE_CLIENT_SECRET")
        creds = Credentials(**token_data)

        service = build("gmail", "v1", credentials=creds)

        results = service.users().messages().list(
            userId="me",
            q="subject:(debit OR credit OR receipt OR payment OR invoice OR transaction OR transfer OR purchase OR airtime)",
            maxResults=30
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
    except Exception as e:
        return JSONResponse(
            {"error": f"Failed to fetch emails"}, 
            status_code=500
        )

    
@router.get("/get_amount")
def get_amount(user: str = Depends(get_current_user)):
    try:
        # Fetch user from MongoDB
        user_doc = user_collection.find_one({"google_id": user})
        if not user_doc or "gmail_token" not in user_doc:
            return JSONResponse(
                {"error": "Gmail credentials not found. Please login with Google first."},
                status_code=401
            )

        token_data = user_doc["gmail_token"]
        token_data = jwt.decode(token_data, SECRET_KEY, algorithms=[ALGORITHM])
        token_data["client_secret"] = os.getenv("GOOGLE_CLIENT_SECRET")
        creds = Credentials(**token_data)
        service = build("gmail", "v1", credentials=creds)

        results = service.users().messages().list(
            userId="me",
            q="subject:(debit OR credit OR receipt OR payment OR invoice OR transaction OR transfer OR purchase OR airtime)",
            maxResults=30
        ).execute()

        messages = results.get("messages", [])
        if not messages:
            return JSONResponse({"matched": [], "total": 0})

        matched = []
        for msg in messages:
            detail = service.users().messages().get(
                userId="me", id=msg["id"], format="full"
            ).execute()

            headers = {
                h.get("name", "").lower(): h.get("value", "")
                for h in detail.get("payload", {}).get("headers", [])
            }
            date_value = headers.get("date")
            if not date_value:
                internal_ms = detail.get("internalDate")
                date_value = (
                    datetime.fromtimestamp(int(internal_ms) / 1000, tz=timezone.utc).isoformat()
                    if internal_ms else "Unknown"
                )

            pre_content = extract_email_body(detail.get("payload", {})) or detail.get("snippet", "Unknown")
            content = clean_email(pre_content)
            subject = headers.get("subject", "No subject")
            from_addr = headers.get("from", "Unknown")

            amount = extract_amount(content)
            if amount is None or len(amount) < 3 or "not" in subject:
                continue
            sender_name = extract_subject_name(from_addr)
            if "reddit" in sender_name.lower() and "reddit-billing@reddit.com" not in sender_name.lower():
                continue

            matched.append({
                "from": sender_name,
                "amount": amount,
                "date": date_value,
                "subject": subject
            })

        return matched

    except Exception as e:
        return JSONResponse({"error": f"Failed to fetch amounts"}, status_code=500)