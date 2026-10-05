from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

Role = Literal["super_admin", "admin"]

PASSWORD_MIN_LENGTH = 8


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class AdminOut(BaseModel):
    id: str
    email: str
    role: Role
    is_active: bool
    invited_at: datetime | None = None
    activated_at: datetime | None = None
    last_login_at: datetime | None = None
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int
    admin: AdminOut


class InvitationCreate(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def lowercase(cls, v: str) -> str:
        return v.lower()


class InvitationOut(BaseModel):
    """A pending invitation = an admins row whose invitation has not been accepted yet."""

    id: str
    email: str
    role: Role
    invited_at: datetime | None
    invited_by_email: str | None = None


class InvitationTokenRequest(BaseModel):
    """access_token is the Supabase token from the invitation link (#access_token=...)."""

    access_token: str = Field(min_length=10)


class InvitationInfo(BaseModel):
    """What the sign-up page shows: who is being set up, and who invited them."""

    email: str
    invited_by_email: str | None


class AcceptInvitationRequest(InvitationTokenRequest):
    password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=72)


class AdminStatusUpdate(BaseModel):
    is_active: bool


class AdminUserList(BaseModel):
    admins: list[AdminOut]
    invitations: list[InvitationOut]
