from supabase import Client, create_client
from supabase_auth.errors import AuthApiError, AuthError

from app.core.config import get_settings

__all__ = ["AuthGateway", "AuthApiError", "AuthError"]


class AuthGateway:
    """All calls to Supabase Auth (auth.users): passwords and invitation emails."""

    def __init__(self, client: Client):
        self.client = client

    def verify_password(self, email: str, password: str) -> str | None:
        """Returns the auth user id if the email/password pair is valid, else None."""
        # sign_in stores the user's session on the client it is called on, which
        # would replace the service-role key for every later query. Use a
        # throwaway client so the shared one is never affected.
        settings = get_settings()
        client = create_client(settings.supabase_url, settings.supabase_service_role_key)
        try:
            res = client.auth.sign_in_with_password({"email": email, "password": password})
        except AuthApiError:
            return None
        return res.user.id if res.user else None

    def invite(self, email: str, redirect_to: str) -> str:
        """Sends Supabase's invitation email and returns the new auth user id."""
        res = self.client.auth.admin.invite_user_by_email(email, {"redirect_to": redirect_to})
        return res.user.id

    def user_from_access_token(self, access_token: str):
        """The auth user that an access token (from the invitation link) belongs to, or None."""
        try:
            res = self.client.auth.get_user(access_token)
        except AuthError:
            return None
        return res.user if res else None

    def set_password(self, user_id: str, password: str) -> None:
        self.client.auth.admin.update_user_by_id(user_id, {"password": password})

    def create_confirmed_user(self, email: str, password: str) -> str:
        res = self.client.auth.admin.create_user(
            {"email": email, "password": password, "email_confirm": True}
        )
        return res.user.id

    def find_user_id_by_email(self, email: str) -> str | None:
        page = 1
        while True:
            users = self.client.auth.admin.list_users(page=page, per_page=200)
            for user in users:
                if (user.email or "").lower() == email:
                    return user.id
            if len(users) < 200:
                return None
            page += 1

    def delete_user(self, user_id: str) -> None:
        self.client.auth.admin.delete_user(user_id)
