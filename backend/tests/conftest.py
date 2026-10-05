import os
from datetime import datetime, timezone
from pathlib import Path

# Test settings must be in place before the app (and its settings) are imported.
# Environment variables take precedence over backend/.env, so the real Supabase
# project is never contacted.
os.environ.update(
    {
        "SUPABASE_URL": "https://test-project.supabase.co",
        "SUPABASE_SERVICE_ROLE_KEY": "test-service-role-key",
        "JWT_SECRET": "test-jwt-secret-that-is-long-enough-for-hs256",
        "JWT_EXPIRE_MINUTES": "60",
        "FRONTEND_URL": "http://frontend.test",
        "QR_BASE_URL": "",
        "CORS_ORIGINS": "http://frontend.test",
    }
)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.config import get_settings  # noqa: E402
from app.core.deps import get_auth_service  # noqa: E402
from app.core.security import create_access_token  # noqa: E402
from app.db.supabase import get_supabase  # noqa: E402
from app.main import app  # noqa: E402
from app.repositories.admin_repository import AdminRepository  # noqa: E402
from app.services.auth_service import AuthService  # noqa: E402
from tests.fakes import FakeAuthGateway, FakeSupabase  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def _fresh_settings():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def db() -> FakeSupabase:
    return FakeSupabase()


@pytest.fixture
def auth_gateway(db) -> FakeAuthGateway:
    return FakeAuthGateway(db)


@pytest.fixture
def client(db, auth_gateway):
    """The real FastAPI app with Supabase (DB + Auth) swapped for in-memory fakes."""
    app.dependency_overrides[get_supabase] = lambda: db
    app.dependency_overrides[get_auth_service] = lambda: AuthService(AdminRepository(db), auth_gateway)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def make_admin(db, auth_gateway):
    """Creates an auth user + admins row. Returns (row, bearer headers)."""

    def _make(email="admin@lumaskin.co", password="password123", role="admin", is_active=True, activated=True):
        user_id = auth_gateway.add_user(email, password)
        row = {
            "id": user_id,
            "email": email,
            "role": role,
            "is_active": is_active,
            "invited_by": None,
            "invited_at": None,
            "activated_at": datetime.now(timezone.utc).isoformat() if activated else None,
            "last_login_at": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        db.tables["admins"].append(row)
        token, _ = create_access_token(user_id, role)
        return row, {"Authorization": f"Bearer {token}"}

    return _make


@pytest.fixture
def admin_headers(make_admin):
    return make_admin("admin@lumaskin.co", role="admin")[1]


@pytest.fixture
def super_admin_headers(make_admin):
    return make_admin("super@lumaskin.co", role="super_admin")[1]


@pytest.fixture
def excel_file():
    def _read(name: str) -> bytes:
        return (FIXTURES / name).read_bytes()

    return _read
