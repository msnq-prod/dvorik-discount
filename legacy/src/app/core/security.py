import hashlib
import hmac
import os
import time


def create_hmac_signature(body: bytes) -> str:
    secret = os.getenv("BOT_HMAC_SECRET", "")
    timestamp = str(int(time.time()))
    message = timestamp.encode() + b"." + body
    signature = hmac.new(
        secret.encode(), msg=message, digestmod=hashlib.sha256
    ).hexdigest()
    return f"{timestamp}.{signature}"


def verify_hmac_signature(signature: str, body: bytes) -> bool:
    secret = os.getenv("BOT_HMAC_SECRET", "")
    try:
        timestamp, sig = signature.split(".")
        message = timestamp.encode() + b"." + body
        expected_signature = hmac.new(
            secret.encode(), msg=message, digestmod=hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_signature, sig)
    except (ValueError, IndexError):
        return False
