"""
Ingest router — /api/ingest
Handles file upload, extraction, AI field parsing, and Firestore persistence.
"""
from __future__ import annotations

import mimetypes
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

import aiofiles  # type: ignore
from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status

from services import firestore_service, gemini_service
from services.conflict_detector import ConflictDetector
from services.extractor import DocumentExtractor
from services.seed_ingestor import ingest_seed_data

router = APIRouter()
_extractor = DocumentExtractor()
_conflict_detector = ConflictDetector()

_SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".png", ".jpg", ".jpeg", ".tiff"}


# ---------------------------------------------------------------------------
# POST /api/ingest/upload
# ---------------------------------------------------------------------------

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    is_seed: bool = Form(False),
):
    """
    Upload a document, extract text + tables, run Gemini field extraction,
    detect conflicts, and persist everything to Firestore.
    """
    filename = file.filename or "unknown_file"
    ext = Path(filename).suffix.lower()

    if ext not in _SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '{ext}'. Supported: {sorted(_SUPPORTED_EXTENSIONS)}",
        )

    # Check for duplicate
    if firestore_service.document_exists_by_filename(filename):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A document named '{filename}' already exists.",
        )

    # Save upload to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp_path = tmp.name

    try:
        async with aiofiles.open(tmp_path, "wb") as out:
            content = await file.read()
            await out.write(content)

        mime_type, _ = mimetypes.guess_type(filename)
        mime_type = mime_type or "application/octet-stream"

        # 1. Extract
        extraction = _extractor.extract(tmp_path, filename, mime_type)
        text: str = extraction["text"]
        tables: list = extraction["tables"]
        doc_type: str = extraction["doc_type"]

        # 2. Gemini field extraction
        doc_id = str(uuid4())
        fields_raw = gemini_service.extract_fields(
            doc_id=doc_id,
            doc_name=filename,
            doc_type=doc_type,
            text=text,
            tables=tables,
        )

        mine_name = next(
            (f["value"] for f in fields_raw if f.get("name") == "mine_name"),
            "",
        )

        fields_with_ids = [
            {
                **f,
                "id": str(uuid4()),
                "doc_id": doc_id,
                "source": filename,
            }
            for f in fields_raw
        ]

        # 3. Build document
        doc_data = {
            "id": doc_id,
            "filename": filename,
            "doc_type": doc_type,
            "mine_name": mine_name,
            "upload_timestamp": datetime.utcnow().isoformat(),
            "fields": fields_with_ids,
            "raw_text": text,
        }

        # 4. Persist document
        firestore_service.save_document(doc_data)

        # 5. Re-run conflict detection across entire corpus
        all_docs = firestore_service.get_all_documents()
        new_conflicts = _conflict_detector.detect_all_conflicts(all_docs)
        for conflict in new_conflicts:
            try:
                firestore_service.save_conflict(conflict)
            except Exception:  # noqa: BLE001
                pass

        # 6. Audit
        firestore_service.save_audit_entry(
            {
                "action": "document_uploaded",
                "user_role": "system" if is_seed else "analyst",
                "doc_id": doc_id,
                "details": f"Uploaded file: {filename}",
            }
        )

        return {
            **doc_data,
            "conflicts_detected": len(new_conflicts),
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {exc}",
        ) from exc
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# GET /api/ingest/documents
# ---------------------------------------------------------------------------

@router.get("/documents")
async def list_documents():
    """Return all ingested documents."""
    try:
        docs = firestore_service.get_all_documents()
        return {"documents": docs, "total": len(docs)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# GET /api/ingest/documents/{doc_id}
# ---------------------------------------------------------------------------

@router.get("/documents/{doc_id}")
async def get_document(doc_id: str):
    """Return a single document by ID."""
    try:
        doc = firestore_service.get_document(doc_id)
        return doc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# GET /api/ingest/needs-review
# ---------------------------------------------------------------------------

@router.get("/needs-review")
async def needs_review():
    """Return all fields across all documents that have flag='needs_review'."""
    try:
        docs = firestore_service.get_all_documents()
        flagged: list[dict] = []
        for doc in docs:
            for field in doc.get("fields") or []:
                if field.get("flag") == "needs_review":
                    flagged.append(
                        {
                            **field,
                            "doc_filename": doc.get("filename"),
                            "doc_type": doc.get("doc_type"),
                        }
                    )
        return {"fields": flagged, "total": len(flagged)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# POST /api/ingest/seed
# ---------------------------------------------------------------------------

@router.post("/seed")
async def trigger_seed():
    """
    Trigger ingestion of all files in ./seed_data/ that have not yet been ingested.
    """
    try:
        ingested_ids = await ingest_seed_data()
        return {
            "message": f"Seed ingestion complete. {len(ingested_ids)} file(s) ingested.",
            "ingested_doc_ids": ingested_ids,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
