from fastapi import Header, HTTPException

from .config import settings


def verify_api_key(x_api_key: str = Header(...)):
    if settings.api_key and x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key
