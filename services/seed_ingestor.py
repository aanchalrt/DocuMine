"""
Seed data ingestor.
Scans ./seed_data/ for supported files and runs the full extraction pipeline
(DocumentExtractor → GeminiService → Firestore) for each file not yet ingested.
Called automatically on startup when the documents collection is empty.
"""
from __future__ import annotations

import mimetypes
import os
from pathlib import Path

from services.extractor import DocumentExtractor
from services import gemini_service
from services import firestore_service
from services.conflict_detector import ConflictDetector

_SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".png", ".jpg", ".jpeg", ".tiff"}

_extractor = DocumentExtractor()
_conflict_detector = ConflictDetector()


async def ingest_seed_data() -> list[str]:
    """
    Walk the ``./seed_data/`` directory and ingest every supported file that
    has not already been persisted (checked by filename).

    Returns a list of ingested doc IDs.
    """
    seed_dir = Path("seed_data")
    if not seed_dir.exists():
        print("[seed_ingestor] seed_data/ directory not found — skipping.")
        return []

    ingested_ids: list[str] = []

    for file_path in sorted(seed_dir.iterdir()):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in _SUPPORTED_EXTENSIONS:
            continue

        filename = file_path.name

        # Skip if already ingested
        try:
            if firestore_service.document_exists_by_filename(filename):
                print(f"[seed_ingestor] '{filename}' already ingested — skipping.")
                continue
        except Exception as exc:  # noqa: BLE001
            print(f"[seed_ingestor] Could not check existence of '{filename}': {exc}")

        print(f"[seed_ingestor] Ingesting '{filename}' …")

        try:
            doc_id = await _ingest_file(str(file_path), filename)
            ingested_ids.append(doc_id)
            print(f"[seed_ingestor] Ingested '{filename}' → doc_id={doc_id}")
        except Exception as exc:  # noqa: BLE001
            print(f"[seed_ingestor] Failed to ingest '{filename}': {exc}")

    # Re-run conflict detection across the whole corpus after all seeds are in
    if ingested_ids:
        try:
            all_docs = firestore_service.get_all_documents()
            conflicts = _conflict_detector.detect_all_conflicts(all_docs)
            for conflict in conflicts:
                firestore_service.save_conflict(conflict)
            print(f"[seed_ingestor] Saved {len(conflicts)} conflict(s).")
        except Exception as exc:  # noqa: BLE001
            print(f"[seed_ingestor] Conflict detection error: {exc}")

    return ingested_ids


async def _ingest_file(file_path: str, filename: str) -> str:
    """Run extraction pipeline on a single file and persist to Firestore."""
    mime_type, _ = mimetypes.guess_type(filename)
    mime_type = mime_type or "application/octet-stream"

    # 1. Extract text / tables
    extraction = _extractor.extract(file_path, filename, mime_type)
    text: str = extraction["text"]
    tables: list = extraction["tables"]
    doc_type: str = extraction["doc_type"]

    # 2. Generate a provisional doc_id and call Gemini for field extraction
    from uuid import uuid4
    doc_id = str(uuid4())

    fields_raw = gemini_service.extract_fields(
        doc_id=doc_id,
        doc_name=filename,
        doc_type=doc_type,
        text=text,
        tables=tables,
    )

    # 3. Find mine_name from extracted fields
    mine_name = next(
        (f["value"] for f in fields_raw if f.get("name") == "mine_name"),
        "",
    )

    # 4. Stamp each field with doc_id and source
    from datetime import datetime

    fields_with_ids = [
        {
            **f,
            "id": str(uuid4()),
            "doc_id": doc_id,
            "source": filename,
        }
        for f in fields_raw
    ]

    # 5. Build document dict
    doc_data = {
        "id": doc_id,
        "filename": filename,
        "doc_type": doc_type,
        "mine_name": mine_name,
        "upload_timestamp": datetime.utcnow().isoformat(),
        "fields": fields_with_ids,
        "raw_text": text,
    }

    # 6. Persist
    firestore_service.save_document(doc_data)

    # 7. Audit entry
    firestore_service.save_audit_entry(
        {
            "action": "document_uploaded",
            "user_role": "system",
            "doc_id": doc_id,
            "details": f"Seed ingestion: {filename}",
        }
    )

    return doc_id
