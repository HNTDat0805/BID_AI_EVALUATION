from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[3] / ".env"),
        env_ignore_empty=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "Bid Document Processing System"

    # Security
    SECRET_KEY: str = "changethis"

    # AI API Keys
    GOOGLE_API_KEY: str = ""

    # PostgreSQL connection string (override via .env file or environment variable)
    DATABASE_URL: str = "postgresql://postgres:123456@localhost:5432/BID-AI-EVALUATION"

    # Stored on disk under the backend folder: ./uploads/{doc_type}/{filename}
    UPLOAD_DIR: str = "uploads"

    # Upload limits
    MAX_UPLOAD_SIZE_MB: int = 5

    # Email
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = "info@example.com"
    EMAILS_FROM_NAME: str = "BID-AI-EVALUATION"
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    # Frontend
    FRONTEND_HOST: str = "http://localhost:5173"

    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def base_dir(self) -> Path:
        return Path(__file__).resolve().parents[2]

    @property
    def upload_dir_path(self) -> Path:
        return (self.base_dir / self.UPLOAD_DIR).resolve()


settings = Settings()  # type: ignore

