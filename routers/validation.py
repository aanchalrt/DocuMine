"""
Validation router — /api/validation
Conflict detection management: list, re-run, and approve conflicts.
"""
from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, Path, status

from services import firestore_service
from services.conflict_detector import ConflictDetector

router = APIRouter()
_conflict_detector = ConflictDetector()


# ---------------------------------------------------------------------------
# GET /api/validation/conflicts
# ---------------------------------------------------------------------------

@router.get("/conflicts")
async def get_conflicts():
    """Return all stored conflict records."""
    try:
        conflicts = firestore_service.get_all_conflicts()
        return {"conflicts": conflicts, "total": len(conflicts)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# POST /api/validation/run
# ---------------------------------------------------------------------------

@router.post("/run")
async def run_conflict_detection():
    """
    Re-run conflict detection across the entire document corpus.
    Clears existing conflict records before saving the new results.
    """
    try:
        all_docs = firestore_service.get_all_documents()
        if not all_docs:
            return {"message": "No documents to analyse.", "conflicts": [], "total": 0}

        # Clear old conflicts
        firestore_service.delete_all_conflicts()

        # Detect
        conflicts = _conflict_detector.detect_all_conflicts(all_docs)

        # Persist
        for conflict in conflicts:
            firestore_service.save_conflict(conflict)

            # Audit each flagged conflict
            firestore_service.save_audit_entry(
                {
                    "action": "conflict_flagged",
                    "user_role": "system",
                    "details": (
                        f"Conflict type: {conflict['conflict_type']}, "
                        f"Parameter: {conflict['parameter']}, "
                        f"Severity: {conflict['severity']}"
                    ),
                }
            )

        return {
            "message": f"Conflict detection complete. {len(conflicts)} conflict(s) found.",
            "conflicts": conflicts,
            "total": len(conflicts),
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# POST /api/validation/approve/{conflict_id}
# ---------------------------------------------------------------------------

@router.post("/approve/{conflict_id}")
async def approve_conflict(
    conflict_id: str = Path(..., description="The conflict record ID to approve"),
    x_user_role: str = Header("analyst", alias="X-User-Role"),
):
    """
    Mark a conflict as reviewed/approved.
    Requires ``X-User-Role: admin`` header.
    """
    if x_user_role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can approve conflicts.",
        )

    try:
        db = firestore_service.get_db()
        ref = db.collection("conflicts").document(conflict_id)
        snap = ref.get()

        if not snap.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conflict '{conflict_id}' not found.",
            )

        ref.update({"status": "approved", "approved_by": "admin"})

        # Audit
        firestore_service.save_audit_entry(
            {
                "action": "document_approved",
                "user_role": "admin",
                "details": f"Conflict approved: {conflict_id}",
            }
        )

        return {
            "message": f"Conflict '{conflict_id}' approved successfully.",
            "conflict_id": conflict_id,
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
