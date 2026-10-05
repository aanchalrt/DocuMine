"""
Audit router — /api/audit
Read and write audit log entries.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from services import firestore_service

router = APIRouter()


# ---------------------------------------------------------------------------
# Request model
# ---------------------------------------------------------------------------

class AuditEntryRequest(BaseModel):
    action: str
    user_role: str = "system"
    doc_id: Optional[str] = None
    details: Optional[str] = None


# ---------------------------------------------------------------------------
# GET /api/audit/log
# ---------------------------------------------------------------------------

@router.get("/log")
async def get_audit_log():
    """Return the 200 most recent audit log entries, ordered by timestamp descending."""
    try:
        entries = firestore_service.get_audit_log(limit=200)
        return {"entries": entries, "total": len(entries)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# POST /api/audit/log
# ---------------------------------------------------------------------------

@router.post("/log", status_code=201)
async def create_audit_entry(body: AuditEntryRequest):
    """
    Manually append an audit log entry.
    Primarily used by internal services; exposed for admin tooling.
    """
    _VALID_ACTIONS = {
        "document_uploaded",
        "report_generated",
        "query_asked",
        "conflict_flagged",
        "document_approved",
    }

    if body.action not in _VALID_ACTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action '{body.action}'. Valid: {sorted(_VALID_ACTIONS)}",
        )

    try:
        entry = body.model_dump()
        entry_id = firestore_service.save_audit_entry(entry)
        return {"id": entry_id, "message": "Audit entry created."}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
