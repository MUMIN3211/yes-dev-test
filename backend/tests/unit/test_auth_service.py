"""Feature 2: AuthService rules (login, invitations, activating/deactivating admins)."""

import pytest
from fastapi import HTTPException

from app.core.security import decode_access_token
from app.repositories.admin_repository import AdminRepository
from app.schemas.auth import AdminOut
from app.services.auth_service import INVALID_INVITE, INVALID_LOGIN, AuthService

pytestmark = pytest.mark.unit


@pytest.fixture
def service(db, auth_gateway) -> AuthService:
    return AuthService(AdminRepository(db), auth_gateway)


@pytest.fixture
def super_admin(make_admin) -> AdminOut:
    return AdminOut(**make_admin("super@lumaskin.co", role="super_admin")[0])


def admin_row(db, email):
    return next((r for r in db.tables["admins"] if r["email"] == email), None)


# --- login ---


def test_login_returns_token_with_role_and_records_last_login(service, make_admin, db):
    row, _ = make_admin("admin@lumaskin.co", "password123", role="admin")
    result = service.login("Admin@LumaSkin.co", "password123")

    assert result.admin.email == "admin@lumaskin.co"
    payload = decode_access_token(result.access_token)
    assert payload["sub"] == row["id"] and payload["role"] == "admin"
    assert admin_row(db, "admin@lumaskin.co")["last_login_at"] is not None


@pytest.mark.parametrize("email, password", [("admin@lumaskin.co", "wrong-password"), ("nobody@lumaskin.co", "password123")])
def test_wrong_password_and_unknown_email_give_the_same_error(service, make_admin, email, password):
    make_admin("admin@lumaskin.co", "password123")
    with pytest.raises(HTTPException) as exc:
        service.login(email, password)
    assert (exc.value.status_code, exc.value.detail) == (401, INVALID_LOGIN)


def test_pending_invitation_cannot_log_in(service, make_admin):
    make_admin("pending@lumaskin.co", "password123", activated=False)
    with pytest.raises(HTTPException) as exc:
        service.login("pending@lumaskin.co", "password123")
    assert exc.value.status_code == 401


def test_deactivated_admin_gets_a_clear_403(service, make_admin):
    make_admin("off@lumaskin.co", "password123", is_active=False)
    with pytest.raises(HTTPException) as exc:
        service.login("off@lumaskin.co", "password123")
    assert exc.value.status_code == 403
    assert "ปิดการใช้งาน" in exc.value.detail


def test_deactivated_admin_with_wrong_password_does_not_learn_the_account_exists(service, make_admin):
    make_admin("off@lumaskin.co", "password123", is_active=False)
    with pytest.raises(HTTPException) as exc:
        service.login("off@lumaskin.co", "wrong")
    assert exc.value.status_code == 401


def test_password_of_another_auth_user_is_not_accepted(service, make_admin, auth_gateway, db):
    # admins row exists, but the auth user that matches the password is a different one
    row, _ = make_admin("admin@lumaskin.co", "password123")
    auth_gateway.users[row["id"]]["password"] = None
    auth_gateway.add_user("admin@lumaskin.co", "password123")
    with pytest.raises(HTTPException) as exc:
        service.login("admin@lumaskin.co", "password123")
    assert exc.value.status_code == 401


# --- invitations ---


def test_invite_sends_email_with_invite_redirect_and_creates_pending_admin(service, super_admin, auth_gateway, db):
    invitation = service.invite("new@lumaskin.co", super_admin)

    assert auth_gateway.invites_sent == [("new@lumaskin.co", "http://frontend.test/invite")]
    assert invitation.email == "new@lumaskin.co"
    assert invitation.role == "admin"  # super admins cannot be invited
    assert invitation.invited_by_email == "super@lumaskin.co"
    row = admin_row(db, "new@lumaskin.co")
    assert row["activated_at"] is None and row["invited_by"] == super_admin.id


def test_inviting_an_existing_admin_is_a_conflict(service, super_admin, make_admin):
    make_admin("admin@lumaskin.co")
    with pytest.raises(HTTPException) as exc:
        service.invite("admin@lumaskin.co", super_admin)
    assert exc.value.status_code == 409


def test_reinviting_replaces_the_old_pending_invitation(service, super_admin, auth_gateway, db):
    first = service.invite("new@lumaskin.co", super_admin)
    old_token = auth_gateway.token_for(first.id)
    second = service.invite("new@lumaskin.co", super_admin)

    assert second.id != first.id
    assert first.id not in auth_gateway.users  # old auth user (and link) removed
    assert [r["id"] for r in db.tables["admins"] if r["email"] == "new@lumaskin.co"] == [second.id]
    with pytest.raises(HTTPException):
        service.get_invitation_info(old_token)


@pytest.mark.parametrize(
    "supabase_error, expected",
    [
        ("Email address not authorized", "Custom SMTP"),
        ("email rate limit exceeded", "rate limit"),
        ("A user with this email address has already been registered", "มีบัญชีอยู่แล้ว"),
        ("Error sending invite email", "SMTP Settings"),
        ("Something else", "ส่งคำเชิญไม่สำเร็จ: Something else"),
    ],
)
def test_supabase_invite_errors_become_readable_502s(service, super_admin, auth_gateway, db, supabase_error, expected):
    auth_gateway.fail_invite_with = supabase_error
    with pytest.raises(HTTPException) as exc:
        service.invite("new@lumaskin.co", super_admin)
    assert exc.value.status_code == 502
    assert expected in exc.value.detail
    assert admin_row(db, "new@lumaskin.co") is None


def test_list_users_separates_admins_from_pending_invitations(service, super_admin, make_admin):
    make_admin("admin@lumaskin.co")
    service.invite("new@lumaskin.co", super_admin)
    result = service.list_users()
    assert {a.email for a in result.admins} == {"super@lumaskin.co", "admin@lumaskin.co"}
    assert [i.email for i in result.invitations] == ["new@lumaskin.co"]
    assert result.invitations[0].invited_by_email == "super@lumaskin.co"


def test_revoke_deletes_pending_invitation(service, super_admin, auth_gateway, db):
    invitation = service.invite("new@lumaskin.co", super_admin)
    service.revoke_invitation(invitation.id)
    assert admin_row(db, "new@lumaskin.co") is None
    assert invitation.id not in auth_gateway.users


def test_revoke_refuses_active_accounts(service, make_admin):
    row, _ = make_admin("admin@lumaskin.co")
    with pytest.raises(HTTPException) as exc:
        service.revoke_invitation(row["id"])
    assert exc.value.status_code == 404


# --- accepting an invitation ---


def test_accept_invitation_sets_password_and_activates(service, super_admin, auth_gateway, db):
    invitation = service.invite("new@lumaskin.co", super_admin)
    token = auth_gateway.token_for(invitation.id)

    info = service.get_invitation_info(token)
    assert (info.email, info.invited_by_email) == ("new@lumaskin.co", "super@lumaskin.co")

    admin = service.accept_invitation(token, "brand-new-password")
    assert admin.activated_at is not None
    assert service.login("new@lumaskin.co", "brand-new-password").admin.id == invitation.id


def test_invitation_link_works_only_once(service, super_admin, auth_gateway):
    invitation = service.invite("new@lumaskin.co", super_admin)
    token = auth_gateway.token_for(invitation.id)
    service.accept_invitation(token, "brand-new-password")
    with pytest.raises(HTTPException) as exc:
        service.accept_invitation(token, "another-password")
    assert (exc.value.status_code, exc.value.detail) == (404, INVALID_INVITE)


def test_unknown_invitation_token_is_rejected(service):
    with pytest.raises(HTTPException) as exc:
        service.get_invitation_info("not-a-real-token")
    assert exc.value.status_code == 404


# --- activate / deactivate ---


def test_super_admin_can_deactivate_and_reactivate_an_admin(service, super_admin, make_admin):
    row, _ = make_admin("admin@lumaskin.co")
    assert service.set_active(row["id"], False, super_admin).is_active is False
    assert service.set_active(row["id"], True, super_admin).is_active is True


def test_cannot_change_own_status(service, super_admin):
    with pytest.raises(HTTPException) as exc:
        service.set_active(super_admin.id, False, super_admin)
    assert exc.value.status_code == 400


def test_cannot_deactivate_another_super_admin(service, super_admin, make_admin):
    other, _ = make_admin("super2@lumaskin.co", role="super_admin")
    with pytest.raises(HTTPException) as exc:
        service.set_active(other["id"], False, super_admin)
    assert exc.value.status_code == 400


def test_cannot_change_status_of_pending_invitation(service, super_admin):
    invitation = service.invite("new@lumaskin.co", super_admin)
    with pytest.raises(HTTPException) as exc:
        service.set_active(invitation.id, False, super_admin)
    assert exc.value.status_code == 404
