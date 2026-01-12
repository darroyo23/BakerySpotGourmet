from datetime import timedelta
from jose import jwt

from bakerySpotGourmet.core import security
from bakerySpotGourmet.core.config import settings

def test_password_hashing():
    password = "testpassword"
    hashed = security.get_password_hash(password)
    assert security.verify_password(password, hashed)
    assert not security.verify_password("wrongpassword", hashed)

def test_access_token():
    subject = "testuser"
    token = security.create_access_token(subject=subject, expires_delta=None)
    decoded = security.decode_token(token)
    assert decoded["sub"] == subject
    assert decoded["type"] == "access"

def test_refresh_token():
    subject = "testuser"
    token = security.create_refresh_token(subject=subject, expires_delta=None)
    decoded = security.decode_token(token)
    assert decoded["sub"] == subject
    assert decoded["type"] == "refresh"
