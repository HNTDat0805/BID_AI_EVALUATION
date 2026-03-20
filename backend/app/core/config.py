from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Keep settings minimal so the Bid Document Processing backend runs locally
    with SQLite by default.
    """

    model_config = SettingsConfigDict(
        # Repo root .env (works regardless of current working directory).
        env_file=str(Path(__file__).resolve().parents[3] / ".env"),
        env_ignore_empty=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "Bid Document Processing System"

    # Local default (required for "runnable locally first")
    DATABASE_URL: str = "sqlite:///./bid_documents.db"

    # Stored on disk under the backend folder: ./uploads/{doc_type}/{filename}
    UPLOAD_DIR: str = "uploads"

    # Upload limits
    MAX_UPLOAD_SIZE_MB: int = 5

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def base_dir(self) -> Path:
        # backend/app/core/config.py -> backend/
        return Path(__file__).resolve().parents[2]

    @property
    def upload_dir_path(self) -> Path:
        return (self.base_dir / self.UPLOAD_DIR).resolve()


settings = Settings()  # type: ignore

