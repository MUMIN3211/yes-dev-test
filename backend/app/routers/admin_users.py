from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.core.deps import get_auth_service, require_super_admin
from app.schemas.auth import (
    AdminOut,
    AdminStatusUpdate,
    AdminUserList,
    InvitationCreate,
    InvitationOut,
)
from app.services.auth_service import AuthService

# Every route here is super_admin only
router = APIRouter(prefix="/api/admin", tags=["admin-users"], dependencies=[Depends(require_super_admin)])


@router.get("/users", response_model=AdminUserList)
def list_users(service: AuthService = Depends(get_auth_service)):
    return service.list_users()


@router.patch("/users/{admin_id}", response_model=AdminOut)
def update_user_status(
    admin_id: UUID,
    body: AdminStatusUpdate,
    actor: AdminOut = Depends(require_super_admin),
    service: AuthService = Depends(get_auth_service),
):
    return service.set_active(str(admin_id), body.is_active, actor)


@router.post("/invitations", response_model=InvitationOut, status_code=201)
def invite_admin(
    body: InvitationCreate,
    actor: AdminOut = Depends(require_super_admin),
    service: AuthService = Depends(get_auth_service),
):
    return service.invite(body.email, actor)


@router.delete("/invitations/{invitation_id}", status_code=204)
def revoke_invitation(invitation_id: UUID, service: AuthService = Depends(get_auth_service)):
    service.revoke_invitation(str(invitation_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
