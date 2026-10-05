from functools import lru_cache

from supabase import Client, create_client

from app.core.config import get_settings


@lru_cache
def get_supabase() -> Client:
    """Single Supabase client for the process, authenticated with the service_role key."""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_service_role_key)
