from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client

from app.core.security import decode_access_token
from app.db.supabase import get_supabase
from app.repositories.admin_repository import AdminRepository
from app.repositories.auth_gateway import AuthGateway
from app.schemas.auth import AdminOut
from app.services.auth_service import AuthService

bearer = HTTPBearer(auto_error=False)


def get_auth_service(client: Client = Depends(get_supabase)) -> AuthService:
    return AuthService(AdminRepository(client), AuthGateway(client))


def get_current_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    client: Client = Depends(get_supabase),
) -> AdminOut:
    """Valid JWT + account still exists, finished its invitation and is active
    (checked on every request, so deactivating an admin takes effect immediately)."""
    unauthorized = HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        "กรุณาเข้าสู่ระบบ",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise unauthorized

    row = AdminRepository(client).get_by_id(payload["sub"])
    if row is None or not row["is_active"] or row["activated_at"] is None:
        raise unauthorized
    return AdminOut(**row)


def require_super_admin(admin: AdminOut = Depends(get_current_admin)) -> AdminOut:
    if admin.role != "super_admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "เฉพาะ Super Admin เท่านั้น")
    return admin
