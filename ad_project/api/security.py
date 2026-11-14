"""Password hashing and JWT helpers."""

import base64
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt

from ad_project.api.config import Settings


def hash_password(password: str) -> str:
    """Hash a password with a per-password random salt."""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return f"pbkdf2_sha256$310000${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password without exposing timing information."""
    try:
        algorithm, rounds_text, salt_text, digest_text = stored_hash.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        rounds = int(rounds_text)
        salt = base64.urlsafe_b64decode(salt_text.encode())
        expected = base64.urlsafe_b64decode(digest_text.encode())
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, rounds)
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: str, role: str, settings: Settings) -> str:
    """Create a short-lived signed access token."""
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_minutes)
    return jwt.encode(
        {"sub": user_id, "role": role, "exp": expires_at},
        settings.jwt_secret_key,
        algorithm="HS256",
    )


def decode_access_token(token: str, settings: Settings) -> dict:
    """Decode and validate a signed access token."""
    return jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
