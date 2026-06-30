from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    database_url: str = Field(
        "postgresql+psycopg2://USER:PASSWORD@HOST.neon.tech/DBNAME?sslmode=require",
        alias="DATABASE_URL",
    )
    openrouter_api_key: str = Field("", alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field(
        "meta-llama/llama-3.1-8b-instruct:free",
        alias="OPENROUTER_MODEL",
    )
    openrouter_site_url: str = Field("http://localhost:8000", alias="OPENROUTER_SITE_URL")
    openrouter_app_name: str = Field("CareerPilot AI", alias="OPENROUTER_APP_NAME")
    auth_secret_key: str = Field("change-this-secret-key", alias="AUTH_SECRET_KEY")
    google_client_id: str = Field("", alias="GOOGLE_CLIENT_ID")
    upload_dir: Path = Field(BASE_DIR / "uploads", alias="UPLOAD_DIR")
    backend_cors_origins: str = Field("", alias="BACKEND_CORS_ORIGINS")

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("upload_dir", mode="before")
    @classmethod
    def resolve_upload_dir(cls, value: str | Path) -> Path:
        path = Path(value)
        if not path.is_absolute():
            path = BASE_DIR / path
        return path

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
