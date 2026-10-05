import logging

from fastapi import HTTPException, status

from app.core.config import get_settings
from app.core.security import create_access_token
from app.repositories.admin_repository import AdminRepository
from app.repositories.auth_gateway import AuthApiError, AuthGateway
from app.schemas.auth import (
    AdminOut,
    AdminUserList,
    InvitationInfo,
    InvitationOut,
    TokenResponse,
)

logger = logging.getLogger(__name__)

# Same message for unknown email and wrong password, so the login form
# cannot be used to discover which emails have accounts.
INVALID_LOGIN = "อีเมลหรือรหัสผ่านไม่ถูกต้อง"
INVALID_INVITE = "ลิงก์คำเชิญไม่ถูกต้อง หมดอายุ หรือถูกใช้งานไปแล้ว กรุณาขอคำเชิญใหม่จาก Super Admin"


def _invite_error_message(err: AuthApiError) -> str:
    text = str(err).lower()
    if "not authorized" in text:
        # Supabase's built-in SMTP only delivers to the project's team members
        return "Supabase ยังส่งอีเมลไปที่อีเมลนี้ไม่ได้ (ระบบอีเมลเริ่มต้นของ Supabase ส่งได้เฉพาะสมาชิกในทีม ต้องตั้งค่า Custom SMTP ก่อน)"
    if "rate limit" in text:
        return "ส่งอีเมลถี่เกินไป (ติด rate limit ของ Supabase) กรุณารอสักครู่แล้วลองใหม่"
    if "already been registered" in text:
        return "อีเมลนี้มีบัญชีอยู่แล้วใน Supabase Auth"
    if "error sending" in text:
        # SMTP server refused the message (e.g. Mailtrap demo domain + non-owner recipient)
        return (
            "Supabase ส่งอีเมลคำเชิญไม่สำเร็จ กรุณาตรวจสอบ SMTP Settings ใน Supabase "
            "และดูรายละเอียดที่ Supabase Dashboard → Logs → Auth"
        )
    return f"ส่งคำเชิญไม่สำเร็จ: {err}"


class AuthService:
    def __init__(self, repo: AdminRepository, auth: AuthGateway):
        self.repo = repo
        self.auth = auth

    # --- login ------------------------------------------------------------

    def login(self, email: str, password: str) -> TokenResponse:
        email = email.lower()
        row = self.repo.get_by_email(email)
        # Only accounts in `admins` that finished their invitation may log in
        if row is None or row["activated_at"] is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, INVALID_LOGIN)
        if self.auth.verify_password(email, password) != row["id"]:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, INVALID_LOGIN)
        if not row["is_active"]:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "บัญชีนี้ถูกปิดการใช้งาน กรุณาติดต่อ Super Admin")

        self.repo.touch_last_login(row["id"])
        token, expires_in = create_access_token(row["id"], row["role"])
        return TokenResponse(access_token=token, expires_in=expires_in, admin=AdminOut(**row))

    # --- admin management (super_admin only; enforced by the router) -------

    def list_users(self) -> AdminUserList:
        rows = self.repo.list_all()
        email_by_id = {r["id"]: r["email"] for r in rows}
        admins = [AdminOut(**r) for r in rows if r["activated_at"] is not None]
        invitations = [
            InvitationOut(**r, invited_by_email=email_by_id.get(r["invited_by"]))
            for r in sorted(rows, key=lambda r: r["invited_at"] or "", reverse=True)
            if r["activated_at"] is None
        ]
        return AdminUserList(admins=admins, invitations=invitations)

    def invite(self, email: str, inviter: AdminOut) -> InvitationOut:
        existing = self.repo.get_by_email(email)
        if existing and existing["activated_at"] is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, "อีเมลนี้มีบัญชีผู้ดูแลอยู่แล้ว")
        if existing:
            # Re-inviting: remove the old pending account so Supabase sends a fresh link
            self.auth.delete_user(existing["id"])

        redirect_to = f"{get_settings().frontend_url.rstrip('/')}/invite"
        try:
            user_id = self.auth.invite(email, redirect_to)
        except AuthApiError as err:
            logger.warning("Supabase invite failed for %s: %s", email, err)
            raise HTTPException(status.HTTP_502_BAD_GATEWAY, _invite_error_message(err)) from err

        row = self.repo.create_pending(user_id, email, "admin", inviter.id)
        return InvitationOut(**row, invited_by_email=inviter.email)

    def revoke_invitation(self, admin_id: str) -> None:
        row = self.repo.get_by_id(admin_id)
        if row is None or row["activated_at"] is not None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบคำเชิญนี้")
        # Deleting the auth user also deletes the admins row (on delete cascade)
        # and makes the emailed link unusable.
        self.auth.delete_user(admin_id)

    def set_active(self, admin_id: str, is_active: bool, actor: AdminOut) -> AdminOut:
        if admin_id == actor.id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "ไม่สามารถเปลี่ยนสถานะบัญชีของตัวเองได้")
        target = self.repo.get_by_id(admin_id)
        if target is None or target["activated_at"] is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "ไม่พบผู้ใช้นี้")
        if target["role"] == "super_admin":
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "ไม่สามารถปิดการใช้งานบัญชี Super Admin ได้")
        return AdminOut(**self.repo.set_active(admin_id, is_active))

    # --- accepting an invitation (public; proven by the Supabase link token) ---

    def _pending_admin_for_token(self, access_token: str) -> dict:
        user = self.auth.user_from_access_token(access_token)
        row = self.repo.get_by_id(user.id) if user else None
        if row is None or row["activated_at"] is not None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, INVALID_INVITE)
        return row

    def get_invitation_info(self, access_token: str) -> InvitationInfo:
        row = self._pending_admin_for_token(access_token)
        inviter = self.repo.get_by_id(row["invited_by"]) if row["invited_by"] else None
        return InvitationInfo(email=row["email"], invited_by_email=inviter["email"] if inviter else None)

    def accept_invitation(self, access_token: str, password: str) -> AdminOut:
        row = self._pending_admin_for_token(access_token)
        try:
            self.auth.set_password(row["id"], password)
        except AuthApiError as err:
            # e.g. Supabase password policy rejected it
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"ตั้งรหัสผ่านไม่สำเร็จ: {err}") from err
        self.repo.mark_activated(row["id"])
        return AdminOut(**self.repo.get_by_id(row["id"]))
