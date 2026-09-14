from datetime import timedelta

import jwt
import pytest


from app.core.security import (
    create_refresh_token,
    get_password_hash,
    get_token_hash,
    verify_password,
    create_access_token,
)
from app.core.config import settings


def test_password_hash_is_different_from_plain_password():
    password = "strong-password"

    hashed_password = get_password_hash(password)

    assert hashed_password != password


def test_correct_password_is_verified():
    password = "strong-password"

    hashed_password = get_password_hash(password)

    assert verify_password(password, hashed_password)


def test_incorrect_password_is_rejected():
    password = "real-password"
    incorrect_password = "fake-password"

    hashed_password = get_password_hash(password)

    assert not verify_password(incorrect_password, hashed_password)


def test_same_token_produces_same_hash():
    token = "test-refresh-token"

    hash_1 = get_token_hash(token)
    hash_2 = get_token_hash(token)

    assert hash_1 == hash_2


def test_token_hash_differs_from_raw_token():
    token = "test-refresh-token"

    token_hash = get_token_hash(token)

    assert token != token_hash


def test_generated_refresh_tokens_are_unique():
    token_1 = create_refresh_token()
    token_2 = create_refresh_token()

    assert token_1 != token_2


def test_access_token_contains_subject():
    token_data = {
        "sub": "42"
    }
    access_token = create_access_token(token_data)

    payload = jwt.decode(
        access_token,
        settings.secret_key, 
        algorithms=[settings.algorithm]
    )

    assert payload["sub"] == token_data["sub"]


def test_access_token_contains_expiration():
    token_data = {
        "sub": "42"
    }
    access_token = create_access_token(token_data)

    payload = jwt.decode(
        access_token, 
        settings.secret_key, 
        algorithms=[settings.algorithm]
    )

    assert "exp" in payload


def test_access_token_does_not_modify_input_data():
    token_data = {
        "sub": "42"
    }
    create_access_token(token_data)

    assert "exp" not in token_data


def test_expired_access_token_is_rejected():
    token_data = {
        "sub": "42",
    }
    access_token = create_access_token(
        token_data,
        expires_delta=timedelta(seconds=-1)
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(
            access_token, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )