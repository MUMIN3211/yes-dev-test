"""Apply supabase/schema.sql (and optionally seed.sql) to the Supabase database.

Usage (from the backend/ folder):
    python scripts/init_db.py           # schema only
    python scripts/init_db.py --seed    # schema + sample products

Reads DATABASE_URL from backend/.env. Both SQL files are idempotent, so
re-running is safe.
"""

import sys
from pathlib import Path

import psycopg
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent
SQL_DIR = BACKEND_DIR.parent / "supabase"


class DbSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    database_url: str


def main() -> None:
    files = ["schema.sql"] + (["seed.sql"] if "--seed" in sys.argv else [])
    url = DbSettings().database_url
    if "[YOUR-PASSWORD]" in url:
        sys.exit("DATABASE_URL in backend/.env still contains [YOUR-PASSWORD]")

    with psycopg.connect(url, autocommit=True) as conn:
        for name in files:
            conn.execute((SQL_DIR / name).read_text(encoding="utf-8"))
            print(f"applied {name}")

        total, active = conn.execute(
            "select count(*), count(*) filter (where status = 'active') from public.products"
        ).fetchone()
        print(f"products: {total} rows ({active} active)")


if __name__ == "__main__":
    main()
