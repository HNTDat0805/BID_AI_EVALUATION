from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlmodel import Session

from ..deps import SessionDep
from ...core.config import settings
from ...crud import (
    create_bid_submission,
    create_document,
    get_bidder,
    get_document,
    get_tender,
    list_documents,
)
from ...models import (
    DocType,
    DocumentRead,
    DocumentUploadResponse,
)
from ...services.extraction import extract_text


router = APIRouter(tags=["documents"])

ALLOWED_UPLOAD_EXTENSIONS = {
    "pdf",
    "docx",
    "xlsx",
    "png",
    "jpg",
}


def _get_extension(filename: str) -> str:
    suffix = Path(filename).suffix.lower().lstrip(".")
    return suffix


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    *,
    file: UploadFile = File(...),
    bidder_id: int = Form(...),
    tender_id: int = Form(...),
    doc_type: DocType = Form(...),
    session: SessionDep,
) -> DocumentUploadResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    file_ext = _get_extension(file.filename)
    if file_ext not in ALLOWED_UPLOAD_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: .{file_ext}. Allowed: {sorted(ALLOWED_UPLOAD_EXTENSIONS)}",
        )

    contents = await file.read()
    if len(contents) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large (max {settings.MAX_UPLOAD_SIZE_MB}MB)",
        )

    doc_type_value = doc_type.value
    safe_filename = Path(file.filename).name
    dest_path = settings.upload_dir_path / doc_type_value / safe_filename
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    tender = get_tender(session, tender_id)
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    bidder = get_bidder(session, bidder_id)
    if not bidder:
        raise HTTPException(status_code=404, detail="Bidder not found")

    # Persist file first (data flow requirement)
    dest_path.write_bytes(contents)

    # Extract content next
    try:
        extracted_text = extract_text(str(dest_path))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(
            status_code=400,
            detail=f"Failed to extract text: {e}",
        ) from e

    # Save metadata to DB
    bid_submission = create_bid_submission(
        session,
        tender_id=tender_id,
        bidder_id=bidder_id,
    )

    file_path_in_db = str(Path(settings.UPLOAD_DIR) / doc_type_value / safe_filename)
    document = create_document(
        session,
        bid_submission_id=bid_submission.id,  # type: ignore[arg-type]
        file_name=safe_filename,
        file_path=file_path_in_db,
        doc_type=doc_type,
        content=extracted_text,
        file_size=len(contents),
    )

    return DocumentUploadResponse(
        file_path=document.file_path,
        extracted_text=document.content or "",
        doc_type=document.doc_type,
    )


@router.get("/documents", response_model=list[DocumentRead])
def get_documents(
    session: SessionDep,
    tender_id: int | None = Query(default=None),
) -> list[DocumentRead]:
    return list_documents(session, tender_id=tender_id)


@router.get("/documents/{id}", response_model=DocumentRead)
def get_document_by_id(
    session: SessionDep,
    id: int,
) -> DocumentRead:
    document = get_document(session, id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

