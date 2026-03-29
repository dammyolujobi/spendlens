from fastapi import APIRouter
from slowapi.util import get_remote_address
from slowapi import Limiter

limiter = Limiter()
router = APIRouter(
    prefix = "sms"
)

@router.get()
async def get_text_message():
    pass