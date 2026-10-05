from datetime import datetime, timezone

from supabase import Client

ADMINS = "admins"
ADMIN_COLUMNS = "id, email, role, is_active, invited_by, invited_at, activated_at, last_login_at, created_at"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AdminRepository:
    """All Supabase access for the `admins` table (role + status of each account)."""

    def __init__(self, client: Client):
        self.client = client

    def get_by_id(self, admin_id: str) -> dict | None:
        rows = self.client.table(ADMINS).select(ADMIN_COLUMNS).eq("id", admin_id).limit(1).execute().data
        return rows[0] if rows else None

    def get_by_email(self, email: str) -> dict | None:
        rows = (
            self.client.table(ADMINS).select(ADMIN_COLUMNS).eq("email", email.lower()).limit(1).execute().data
        )
        return rows[0] if rows else None

    def list_all(self) -> list[dict]:
        return self.client.table(ADMINS).select(ADMIN_COLUMNS).order("created_at").execute().data

    def create_pending(self, admin_id: str, email: str, role: str, invited_by: str) -> dict:
        row = {
            "id": admin_id,
            "email": email.lower(),
            "role": role,
            "invited_by": invited_by,
            "invited_at": _now(),
        }
        return self.client.table(ADMINS).insert(row).execute().data[0]

    def upsert_active(self, admin_id: str, email: str, role: str) -> dict:
        row = {
            "id": admin_id,
            "email": email.lower(),
            "role": role,
            "is_active": True,
            "activated_at": _now(),
        }
        return self.client.table(ADMINS).upsert(row, on_conflict="id").execute().data[0]

    def mark_activated(self, admin_id: str) -> None:
        self.client.table(ADMINS).update({"activated_at": _now()}).eq("id", admin_id).execute()

    def set_active(self, admin_id: str, is_active: bool) -> dict | None:
        rows = self.client.table(ADMINS).update({"is_active": is_active}).eq("id", admin_id).execute().data
        return rows[0] if rows else None

    def touch_last_login(self, admin_id: str) -> None:
        self.client.table(ADMINS).update({"last_login_at": _now()}).eq("id", admin_id).execute()
