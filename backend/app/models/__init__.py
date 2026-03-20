from enum import Enum
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import DateTime, Text as SQLAText
from sqlalchemy.orm import Mapped
from sqlmodel import Field, Relationship, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DocType(str, Enum):
    # Document classification for tender evaluation.
    legal = "legal"
    financial = "financial"
    technical = "technical"
    experience = "experience"
    personnel = "personnel"
    equipment = "equipment"
    methodology = "methodology"
    other = "other"


# -----------------------
# Database Models (tables)
# -----------------------


class Tender(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None

    bid_submissions: Mapped[List["BidSubmission"]] = Relationship(
        back_populates="tender"
    )


class Bidder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str

    bid_submissions: Mapped[List["BidSubmission"]] = Relationship(
        back_populates="bidder"
    )


class BidSubmission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tender_id: int = Field(foreign_key="tender.id", nullable=False)
    bidder_id: int = Field(foreign_key="bidder.id", nullable=False)
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    tender: Mapped[Optional[Tender]] = Relationship(back_populates="bid_submissions")
    bidder: Mapped[Optional[Bidder]] = Relationship(back_populates="bid_submissions")

    documents: Mapped[List["Document"]] = Relationship(
        back_populates="bid_submission", cascade_delete=True
    )
    evaluation_results: Mapped[List["EvaluationResult"]] = Relationship(
        back_populates="bid_submission", cascade_delete=True
    )


class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bid_submission_id: int = Field(
        foreign_key="bidsubmission.id", nullable=False
    )

    file_name: str
    file_path: str
    doc_type: DocType = Field(index=True)
    content: Optional[str] = Field(default=None, sa_type=SQLAText)
    file_size: int
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_type=DateTime(timezone=True),  # type: ignore
    )

    bid_submission: Mapped[Optional[BidSubmission]] = Relationship(
        back_populates="documents"
    )


class EvaluationResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    bid_submission_id: int = Field(
        foreign_key="bidsubmission.id", nullable=False
    )
    score: float
    result: str

    bid_submission: Mapped[Optional[BidSubmission]] = Relationship(
        back_populates="evaluation_results"
    )


class Criteria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tender_id: int = Field(foreign_key="tender.id", nullable=False)
    name: str
    weight: float


# -----------------------
# Response Schemas (non-table)
# -----------------------


class DocumentRead(SQLModel):
    id: int
    bid_submission_id: int
    file_name: str
    file_path: str
    doc_type: DocType
    content: Optional[str] = None
    file_size: int
    created_at: datetime


class DocumentUploadResponse(SQLModel):
    file_path: str
    extracted_text: str
    doc_type: DocType


class EvaluationRunResponse(SQLModel):
    status: str
    message: str

