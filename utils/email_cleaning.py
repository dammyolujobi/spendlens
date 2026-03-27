from bs4 import BeautifulSoup
import re
import base64
def clean_email(content):
    soup = BeautifulSoup(content, "html.parser")
    text = soup.get_text()
    return re.sub(r'\s+', ' ', text).strip()


def _decode_base64url(data: str) -> str:
    if not data:
        return ""
    data += "=" * (-len(data) % 4)  # fix missing padding
    return base64.urlsafe_b64decode(data.encode("utf-8")).decode("utf-8", errors="ignore")


def extract_email_body(payload: dict) -> str:
    # 1) direct body
    body_data = payload.get("body", {}).get("data")
    if body_data:
        return _decode_base64url(body_data).strip()

  
    for part in payload.get("parts", []) or []:
        mime = part.get("mimeType", "")
        data = part.get("body", {}).get("data")
        if data and mime in ("text/plain", "text/html"):
            return _decode_base64url(data).strip()

        # nested multipart
        for sub in part.get("parts", []) or []:
            sub_mime = sub.get("mimeType", "")
            sub_data = sub.get("body", {}).get("data")
            if sub_data and sub_mime in ("text/plain", "text/html"):
                return _decode_base64url(sub_data).strip()

    return ""

def extract_amount(text:str):
    patterns = [
        r'₦\s?([\d,]+\.?\d*)',
        r'\$\s?([\d,]+\.?\d*)',
        r'N\s?([\d,]+\.?\d*)',
        r'Credit Amount\s*([\d,]+\.?\d*)',
        r'Debit Amount\s*([\d,]+\.?\d*)'
    ]

    for pattern in patterns:
        match = re.search(pattern,text,re.IGNORECASE)
        if match:
            return (match.group(1).replace(',',''))
    
    return None

def extract_subject_name(text:str)->str:
    result = re.findall(r'^[^ ]*',text)
    return result[0]