import jwt
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from jwt.exceptions import InvalidTokenError
from app.core.config import Settings


password_hash = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return password_hash.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=Settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Settings.secret_key, algorithm=Settings.algorithm)
    return encoded_jwt