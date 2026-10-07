"""
CodeSecure AI — Authentication Engine
Provides cryptographic password hashing (PBKDF2-HMAC-SHA256) and JWT session handling.
"""

import base64
import hashlib
import hmac
import json
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple
from app.config import settings
from app.utils.logging_utils import get_logger

logger = get_logger("authentication")


def hash_password(password: str, salt: Optional[bytes] = None) -> str:
    """
    Hashes a password using PBKDF2-HMAC-SHA256 with a 16-byte random salt and 600,000 iterations.
    Format: pbkdf2_sha256$<iterations>$<salt_b64>$<hash_b64>
    """
    if salt is None:
        salt = os.urandom(16)
    iterations = 600_000
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    salt_b64 = base64.b64encode(salt).decode("ascii")
    hash_b64 = base64.b64encode(derived).decode("ascii")
    return f"pbkdf2_sha256${iterations}${salt_b64}${hash_b64}"


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """
    Verifies a plain-text password against a stored PBKDF2 hash using constant-time comparison.
    """
    try:
        parts = stored_hash.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            # Fallback check for raw SHA-256 for legacy or test hashes
            if len(stored_hash) == 64:
                expected = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
                return hmac.compare_digest(expected, stored_hash)
            return False

        iterations = int(parts[1])
        salt = base64.b64decode(parts[2].encode("ascii"))
        expected_derived = base64.b64decode(parts[3].encode("ascii"))

        actual_derived = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(actual_derived, expected_derived)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def _b64_url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64_url_decode(data: str) -> bytes:
    padding = "=" * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("ascii"))


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a secure HS256 JWT token for session authentication.
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"iat": int(now.timestamp()), "exp": int(expire.timestamp())})

    header = {"alg": "HS256", "typ": "JWT"}
    header_json = json.dumps(header, separators=(",", ":")).encode("utf-8")
    payload_json = json.dumps(to_encode, separators=(",", ":")).encode("utf-8")

    header_b64 = _b64_url_encode(header_json)
    payload_b64 = _b64_url_encode(payload_json)

    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    signature = hmac.new(settings.SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64_url_encode(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifies a JWT token signature and expiration, returning the payload if valid.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None

        header_b64, payload_b64, sig_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
        expected_sig = hmac.new(settings.SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
        actual_sig = _b64_url_decode(sig_b64)

        if not hmac.compare_digest(expected_sig, actual_sig):
            logger.warning("Token signature verification failed.")
            return None

        payload_bytes = _b64_url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))

        # Check expiration
        exp = payload.get("exp")
        if exp and int(time.time()) > exp:
            logger.warning("Token has expired.")
            return None

        return payload
    except Exception as e:
        logger.warning(f"Token decoding error: {e}")
        return None
