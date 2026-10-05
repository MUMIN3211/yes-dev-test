from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]

# backend/.env, resolved from this file so it loads no matter where uvicorn is started
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore")

    supabase_url: str
    supabase_service_role_key: str
    cors_origins: str = "http://localhost:3000"

    # Auth (Feature 2)
    jwt_secret: str
    jwt_expire_minutes: int = 480
    # Base URL of the Next.js app. Supabase invitation emails link back to {frontend_url}/invite
    frontend_url: str = "http://localhost:3000"

    @model_validator(mode="after")
    def reject_placeholders(self) -> "Settings":
        # Fail fast with a clear message instead of a confusing DNS/auth error later
        placeholders = {
            "SUPABASE_URL": "your-project-ref" in self.supabase_url,
            "SUPABASE_SERVICE_ROLE_KEY": self.supabase_service_role_key
            in ("your-service-role-key", "PASTE_SERVICE_ROLE_KEY_HERE"),
            "JWT_SECRET": self.jwt_secret == "change-me",
        }
        missing = [name for name, is_placeholder in placeholders.items() if is_placeholder]
        if missing:
            raise ValueError(f"backend/.env still has placeholder values for: {', '.join(missing)}")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
