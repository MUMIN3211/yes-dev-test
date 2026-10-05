"""Create (or reset) a super_admin account. There is no sign-up page, so this
is how the first account is made.

Usage (from the backend/ folder):
    python scripts/create_super_admin.py <email> <password>

Creates a confirmed Supabase Auth user (no email is sent) plus its `admins`
row. If the email already exists, its password is reset, role set to
super_admin and the account re-activated.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.supabase import get_supabase  # noqa: E402
from app.repositories.admin_repository import AdminRepository  # noqa: E402
from app.repositories.auth_gateway import AuthGateway  # noqa: E402
from app.schemas.auth import PASSWORD_MIN_LENGTH  # noqa: E402


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    email, password = sys.argv[1].strip().lower(), sys.argv[2]
    if len(password) < PASSWORD_MIN_LENGTH:
        sys.exit(f"Password must be at least {PASSWORD_MIN_LENGTH} characters")

    client = get_supabase()
    auth = AuthGateway(client)
    user_id = auth.find_user_id_by_email(email)
    if user_id:
        auth.set_password(user_id, password)
    else:
        user_id = auth.create_confirmed_user(email, password)

    AdminRepository(client).upsert_active(user_id, email, "super_admin")
    print(f"super_admin ready: {email}")


if __name__ == "__main__":
    main()
