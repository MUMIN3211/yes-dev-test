from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import get_settings

JWT_ALGORITHM = "HS256"

# Passwords live in Supabase Auth. After Supabase verifies them, the backend
# issues its own short JWT that carries the admin id and role.


def create_access_token(admin_id: str, role: str) -> tuple[str, int]:
    """Returns (token, expires_in_seconds)."""
    settings = get_settings()
    expires_in = settings.jwt_expire_minutes * 60
    now = datetime.now(timezone.utc)
    payload = {
        "sub": admin_id,
        "role": role,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM), expires_in


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, get_settings().jwt_secret, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None
