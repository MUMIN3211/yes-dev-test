from fastapi import APIRouter, Depends

from app.core.deps import get_auth_service, get_current_admin
from app.schemas.auth import (
    AcceptInvitationRequest,
    AdminOut,
    InvitationInfo,
    InvitationTokenRequest,
    LoginRequest,
    TokenResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, service: AuthService = Depends(get_auth_service)):
    return service.login(body.email, body.password)


@router.get("/me", response_model=AdminOut)
def me(admin: AdminOut = Depends(get_current_admin)):
    return admin


# The invitation endpoints take the Supabase access token from the emailed link
# in the request body (POST) so it never ends up in URLs or server logs.


@router.post("/invitation", response_model=InvitationInfo)
def get_invitation(body: InvitationTokenRequest, service: AuthService = Depends(get_auth_service)):
    """Used by the sign-up page to show which email is being set up and who invited it."""
    return service.get_invitation_info(body.access_token)


@router.post("/invitation/accept", response_model=AdminOut)
def accept_invitation(body: AcceptInvitationRequest, service: AuthService = Depends(get_auth_service)):
    return service.accept_invitation(body.access_token, body.password)
