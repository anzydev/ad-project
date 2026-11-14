"""Focused tests for backend security helpers and configuration validation."""

import jwt
import pytest

from ad_project.api.config import Settings
from ad_project.api.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hashes_are_salted_and_verifiable():
    first = hash_password("correct horse battery staple")
    second = hash_password("correct horse battery staple")

    assert first != second
    assert verify_password("correct horse battery staple", first)
    assert not verify_password("wrong password", first)


def test_access_token_contains_identity_and_rejects_tampering():
    settings = Settings(jwt_secret_key="a" * 32)
    token = create_access_token("user-123", "USER", settings)

    assert decode_access_token(token, settings)["sub"] == "user-123"
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token + "tampered", settings)
