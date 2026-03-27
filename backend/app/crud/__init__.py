from __future__ import annotations

from typing import Optional

from sqlmodel import Session, select

from ..models import (
    Bidder,
    BidSubmission,
    Criteria,
    Document,
    EvaluationResult,
    Tender,
    DocType,
)


def get_tender(session: Session, tender_id: int) -> Optional[Tender]:
    return session.get(Tender, tender_id)


def get_bidder(session: Session, bidder_id: int) -> Optional[Bidder]:
    return session.get(Bidder, bidder_id)


def create_bid_submission(
    session: Session, *, tender_id: int, bidder_id: int
) -> BidSubmission:
    bid_submission = BidSubmission(tender_id=tender_id, bidder_id=bidder_id)
    session.add(bid_submission)
    session.flush()  # populate bid_submission.id without a full commit
    session.refresh(bid_submission)
    return bid_submission


def create_document(
    session: Session,
    *,
    bid_submission_id: int,
    file_name: str,
    file_path: str,
    doc_type: DocType,
    content: str | None,
    file_size: int,
) -> Document:
    document = Document(
        bid_submission_id=bid_submission_id,
        file_name=file_name,
        file_path=file_path,
        doc_type=doc_type,
        content=content,
        file_size=file_size,
    )
    session.add(document)
    session.flush()
    session.refresh(document)
    return document


def get_document(session: Session, document_id: int) -> Optional[Document]:
    return session.get(Document, document_id)


def list_documents(session: Session, *, tender_id: int | None) -> list[Document]:
    statement = select(Document)
    if tender_id is not None:
        statement = statement.join(BidSubmission).where(
            BidSubmission.tender_id == tender_id
        )
    statement = statement.order_by(Document.created_at.desc())
    return session.exec(statement).all()


# Placeholder CRUD for future Evaluation module expansion
def create_evaluation_result(
    session: Session,
    *,
    bid_submission_id: int,
    score: float,
    result: str,
) -> EvaluationResult:
    evaluation = EvaluationResult(
        bid_submission_id=bid_submission_id,
        score=score,
        result=result,
    )
    session.add(evaluation)
    session.flush()
    session.refresh(evaluation)
    return evaluation


def create_criteria(
    session: Session, *, tender_id: int, name: str, weight: float
) -> Criteria:
    criteria = Criteria(tender_id=tender_id, name=name, weight=weight)
    session.add(criteria)
    session.flush()
    session.refresh(criteria)
    return criteria

