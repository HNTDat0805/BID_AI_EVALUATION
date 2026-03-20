from __future__ import annotations

from sqlmodel import SQLModel, Session, create_engine, select

from .config import settings


def _create_engine():
    # SQLite needs this for multithreaded environments (dev server).
    if settings.DATABASE_URL.startswith("sqlite"):
        return create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False},
        )
    try:
        return create_engine(settings.DATABASE_URL)
    except (ModuleNotFoundError, ImportError) as e:
        # If Postgres driver isn't installed yet (e.g. during a broken image build),
        # allow the app to start by falling back to SQLite.
        # This prevents container hard-crashes and makes local development smoother.
        if (
            ("psycopg2" in str(e).lower() or "psycopg" in str(e).lower())
            and settings.DATABASE_URL.startswith("postgres")
        ):
            fallback_url = "sqlite:///./bid_documents.db"
            return create_engine(
                fallback_url,
                connect_args={"check_same_thread": False},
            )
        raise


engine = _create_engine()


def init_db() -> None:
    # Import models so SQLModel registers table metadata.
    from .. import models as _models  # noqa: F401

    SQLModel.metadata.create_all(engine)

    # Seed minimal data so the upload endpoint is runnable immediately
    # in development (tender_id=1, bidder_id=1).
    from ..models import Bidder, Tender

    with Session(engine) as session:
        has_tender = session.exec(select(Tender).limit(1)).first()
        has_bidder = session.exec(select(Bidder).limit(1)).first()

        if has_tender and has_bidder:
            return

        if not has_tender:
            session.add(
                Tender(
                    name="Default Tender",
                    description="Seeded for local development",
                )
            )
        if not has_bidder:
            session.add(
                Bidder(
                    name="Default Bidder",
                    email="default-bidder@example.com",
                )
            )

        session.commit()


def get_session() -> Session:
    return Session(engine)

