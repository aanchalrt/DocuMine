"""
Firestore persistence service for DocuMine.
Uses firebase-admin with lazy initialisation (supports both service-account
JSON and Application Default Credentials).
"""
from __future__ import annotations

import os
from datetime import datetime
from typing import Optional
from uuid import uuid4

import firebase_admin  # type: ignore
from firebase_admin import credentials, firestore as fs_admin  # type: ignore

# ---------------------------------------------------------------------------
# Lazy DB initialisation
# ---------------------------------------------------------------------------

_db: Optional[object] = None


def get_db():
    """Return (and lazily initialise) the Firestore client."""
    global _db
    if _db is None:
        if not firebase_admin._apps:
            cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                # Use Application Default Credentials (e.g. Cloud Run / GCE)
                firebase_admin.initialize_app()
        _db = fs_admin.client()
    return _db


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _doc_to_dict(doc_snapshot) -> dict:
    """Convert a Firestore DocumentSnapshot to a plain Python dict."""
    data = doc_snapshot.to_dict() or {}
    data["id"] = doc_snapshot.id
    return data


# ---------------------------------------------------------------------------
# Documents collection
# ---------------------------------------------------------------------------

def save_document(doc_data: dict) -> str:
    """
    Persist an extracted document to the ``documents`` Firestore collection.

    If doc_data already contains an ``id`` field that key is used as the
    Firestore document ID; otherwise a new UUID is generated.

    Returns the document ID.
    """
    db = get_db()
    doc_id: str = doc_data.get("id") or str(uuid4())
    doc_data["id"] = doc_id

    # Firestore cannot serialise custom objects — ensure everything is plain
    doc_ref = db.collection("documents").document(doc_id)
    doc_ref.set(doc_data)
    return doc_id


def get_all_documents() -> list[dict]:
    """Return every document in the ``documents`` collection."""
    db = get_db()
    docs = db.collection("documents").stream()
    return [_doc_to_dict(d) for d in docs]


def get_document(doc_id: str) -> dict:
    """
    Return a single document by ID.

    Raises ``KeyError`` if the document does not exist.
    """
    db = get_db()
    doc_ref = db.collection("documents").document(doc_id).get()
    if not doc_ref.exists:
        raise KeyError(f"Document '{doc_id}' not found in Firestore")
    return _doc_to_dict(doc_ref)


def document_exists_by_filename(filename: str) -> bool:
    """Return True if a document with this filename already exists."""
    db = get_db()
    results = (
        db.collection("documents")
        .where("filename", "==", filename)
        .limit(1)
        .stream()
    )
    return any(True for _ in results)


# ---------------------------------------------------------------------------
# Conflicts collection
# ---------------------------------------------------------------------------

def save_conflict(conflict: dict) -> str:
    """
    Persist a conflict record to the ``conflicts`` collection.

    Returns the conflict ID.
    """
    db = get_db()
    conflict_id: str = conflict.get("id") or str(uuid4())
    conflict["id"] = conflict_id
    db.collection("conflicts").document(conflict_id).set(conflict)
    return conflict_id


def get_all_conflicts() -> list[dict]:
    """Return every conflict record."""
    db = get_db()
    docs = db.collection("conflicts").stream()
    return [_doc_to_dict(d) for d in docs]


def delete_all_conflicts() -> None:
    """Remove all conflict records (used before a fresh re-run)."""
    db = get_db()
    batch = db.batch()
    for doc in db.collection("conflicts").stream():
        batch.delete(doc.reference)
    batch.commit()


# ---------------------------------------------------------------------------
# Audit log collection
# ---------------------------------------------------------------------------

def save_audit_entry(entry: dict) -> str:
    """
    Append an immutable audit log entry to the ``audit_log`` collection.

    Returns the entry ID.
    """
    db = get_db()
    entry_id: str = entry.get("id") or str(uuid4())
    entry["id"] = entry_id
    if "timestamp" not in entry:
        entry["timestamp"] = datetime.utcnow().isoformat()
    db.collection("audit_log").document(entry_id).set(entry)
    return entry_id


def get_audit_log(limit: int = 100) -> list[dict]:
    """
    Return the most recent audit log entries ordered by timestamp descending.
    """
    db = get_db()
    docs = (
        db.collection("audit_log")
        .order_by("timestamp", direction=fs_admin.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    return [_doc_to_dict(d) for d in docs]
