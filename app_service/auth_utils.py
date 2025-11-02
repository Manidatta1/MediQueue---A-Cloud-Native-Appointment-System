import os, requests
from fastapi import Header, HTTPException
import logging
import logging
import sys
# ---------------------------------------------------------------------
# 🧩 LOGGING CONFIGURATION
# ---------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Attach handler to write to stdout (ensures Docker can capture)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
handler.setFormatter(formatter)

# Avoid duplicate handlers
if not logger.handlers:
    logger.addHandler(handler)

logger.info("✅ auth_utils.py loaded successfully")

AUTH_VERIFY_URL = os.getenv("AUTH_VERIFY_URL", "http://auth_service:8001/verify-token")

def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    try:
        res = requests.get(AUTH_VERIFY_URL, headers={"Authorization": authorization}, timeout=5)
        if res.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        data = res.json()
        return data.get("claims", {})
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Auth verification failed: {str(e)}")

def verify_token_remote(auth_header: str):
    logger.info(f"🪪 Raw Authorization header received: {auth_header}")

    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        # Pass the token exactly as received
        headers = {"Authorization": auth_header}
        response = requests.get(AUTH_VERIFY_URL, headers=headers)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail", "Invalid or expired token"))

        return response.json()["claims"]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auth service error: {e}")