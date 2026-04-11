"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent


class Settings(BaseSettings):
    """Centralized settings for runtime configuration."""

    app_name: str = "AI Crime Analytics Platform"
    app_version: str = "1.0.0"
    api_prefix: str = "/api"
    environment: str = "development"
    allowed_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    log_level: str = "INFO"
    database_dir: Path = PROJECT_ROOT / "Database"
    csv_filename: str = "India_Crime_Dataset_StateWise_2000_2025.csv"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="CRIME_ANALYTICS_",
        case_sensitive=False,
    )

    @property
    def preferred_csv_path(self) -> Path:
        """Return the configured CSV path within the Database directory."""

        return self.database_dir / self.csv_filename


@lru_cache
def get_settings() -> Settings:
    """Cache settings so they are created once per process."""

    return Settings()
