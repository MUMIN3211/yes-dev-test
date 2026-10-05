"""Feature 2 building blocks: JWT helpers, settings validation and request schemas."""

from datetime import datetime, timedelta, timezone

import jwt
import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings
from app.core.security import JWT_ALGORITHM, create_access_token, decode_access_token
from app.schemas.auth import AcceptInvitationRequest, InvitationCreate, LoginRequest

pytestmark = pytest.mark.unit


# --- JWT ---


def test_token_round_trip_carries_admin_id_and_role():
    token, expires_in = create_access_token("admin-id", "super_admin")
    payload = decode_access_token(token)
    assert payload["sub"] == "admin-id"
    assert payload["role"] == "super_admin"
    assert expires_in == 60 * 60  # JWT_EXPIRE_MINUTES=60 in conftest
    assert payload["exp"] - payload["iat"] == expires_in


def test_expired_token_is_rejected():
    secret = get_settings().jwt_secret
    past = datetime.now(timezone.utc) - timedelta(minutes=5)
    token = jwt.encode({"sub": "x", "role": "admin", "iat": past, "exp": past}, secret, algorithm=JWT_ALGORITHM)
    assert decode_access_token(token) is None


def test_token_signed_with_another_secret_is_rejected():
    token = jwt.encode({"sub": "x", "role": "super_admin"}, "attacker-secret-attacker-secret!!", algorithm=JWT_ALGORITHM)
    assert decode_access_token(token) is None


def test_tampered_token_is_rejected():
    token, _ = create_access_token("admin-id", "admin")
    header, payload, signature = token.split(".")
    assert decode_access_token(f"{header}.{payload}x.{signature}") is None


@pytest.mark.parametrize("token", ["", "garbage", "a.b.c"])
def test_malformed_token_is_rejected(token):
    assert decode_access_token(token) is None


def test_unsigned_none_algorithm_token_is_rejected():
    token = jwt.encode({"sub": "x", "role": "super_admin"}, key=None, algorithm="none")
    assert decode_access_token(token) is None


# --- settings ---


BASE = {
    "supabase_url": "https://abc.supabase.co",
    "supabase_service_role_key": "real-key",
    "jwt_secret": "real-secret",
    "_env_file": None,
}


@pytest.mark.parametrize(
    "override, name",
    [
        ({"supabase_url": "https://your-project-ref.supabase.co"}, "SUPABASE_URL"),
        ({"supabase_service_role_key": "your-service-role-key"}, "SUPABASE_SERVICE_ROLE_KEY"),
        ({"jwt_secret": "change-me"}, "JWT_SECRET"),
    ],
)
def test_placeholder_values_from_env_example_are_rejected(override, name):
    with pytest.raises(ValidationError) as exc:
        Settings(**{**BASE, **override})
    assert name in str(exc.value)


def test_cors_origins_are_split_and_trimmed():
    settings = Settings(**BASE, cors_origins=" http://a.test , http://b.test,, ")
    assert settings.cors_origin_list == ["http://a.test", "http://b.test"]


def test_public_site_url_prefers_qr_base_url():
    assert Settings(**BASE, frontend_url="http://f.test/").public_site_url == "http://f.test"
    assert Settings(**BASE, frontend_url="http://f.test", qr_base_url="http://q.test/").public_site_url == "http://q.test"


# --- request schemas ---


def test_invitation_email_is_lowercased():
    assert InvitationCreate(email="New.Admin@LumaSkin.CO").email == "new.admin@lumaskin.co"


@pytest.mark.parametrize("email", ["not-an-email", "", "a@"])
def test_invalid_emails_are_rejected(email):
    with pytest.raises(ValidationError):
        LoginRequest(email=email, password="x")


@pytest.mark.parametrize("password, ok", [("1234567", False), ("12345678", True), ("x" * 72, True), ("x" * 73, False)])
def test_new_password_length_rules(password, ok):
    if ok:
        AcceptInvitationRequest(access_token="t" * 20, password=password)
    else:
        with pytest.raises(ValidationError):
            AcceptInvitationRequest(access_token="t" * 20, password=password)
