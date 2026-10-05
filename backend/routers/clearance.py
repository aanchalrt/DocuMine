"""
Clearance router — /api/clearance
Displays regulatory NOC / clearance correspondence as an ordered timeline,
highlighting bottlenecks by days pending.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from services import firestore_service

router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_date(date_str: str) -> Optional[date]:
    """Try multiple common date formats; return None on failure."""
    for fmt in (
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%B %d, %Y",
        "%d %B %Y",
        "%b %d, %Y",
        "%d %b %Y",
    ):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except (ValueError, AttributeError):
            continue
    return None


def _get_field_value(fields: list[dict], name: str) -> str:
    """Return the value of the first field matching ``name``, or ''."""
    for f in fields:
        if f.get("name") == name:
            return f.get("value") or ""
    return ""


# ---------------------------------------------------------------------------
# GET /api/clearance/timeline
# ---------------------------------------------------------------------------

@router.get("/timeline")
async def get_clearance_timeline():
    """
    Return all correspondence-type documents as an ordered clearance timeline.

    For each document:
    - Extracts sender_office, recipient_office, date, subject, status fields.
    - Calculates days_pending as days elapsed since the document date.
    - Marks the step with the highest days_pending as the bottleneck.

    Returns steps sorted by date ascending (earliest first).
    """
    try:
        all_docs = firestore_service.get_all_documents()
        correspondence_docs = [
            d for d in all_docs if d.get("doc_type") == "correspondence"
        ]

        if not correspondence_docs:
            return {
                "timeline": [],
                "bottleneck_id": None,
                "total": 0,
            }

        steps: list[dict] = []
        today = date.today()

        for doc in correspondence_docs:
            fields = doc.get("fields") or []
            doc_id = doc.get("id", str(uuid4()))

            sender_office = _get_field_value(fields, "sender_office")
            recipient_office = _get_field_value(fields, "recipient_office")
            doc_date_str = _get_field_value(fields, "report_date") or _get_field_value(
                fields, "date"
            )
            subject = _get_field_value(fields, "subject")
            status_val = _get_field_value(fields, "status") or "pending"

            # Normalise status
            status_val = status_val.lower().strip()
            if status_val not in {"pending", "resolved", "escalated"}:
                status_val = "pending"

            # Calculate days pending
            days_pending: Optional[int] = None
            parsed_date = _parse_date(doc_date_str)
            if parsed_date:
                days_pending = (today - parsed_date).days

            steps.append(
                {
                    "id": doc_id,
                    "doc_id": doc_id,
                    "sender_office": sender_office,
                    "recipient_office": recipient_office,
                    "date": doc_date_str,
                    "subject": subject,
                    "status": status_val,
                    "days_pending": days_pending,
                    "filename": doc.get("filename", ""),
                    "mine_name": doc.get("mine_name", ""),
                    "is_bottleneck": False,
                }
            )

        # Sort by date ascending (steps with no parsed date go last)
        def sort_key(step: dict):
            d = _parse_date(step.get("date") or "")
            return d.toordinal() if d else 9999999

        steps.sort(key=sort_key)

        # Mark bottleneck — step with highest days_pending (among pending steps)
        bottleneck_id: Optional[str] = None
        max_pending: Optional[int] = None

        for step in steps:
            dp = step.get("days_pending")
            if dp is not None and step["status"] == "pending":
                if max_pending is None or dp > max_pending:
                    max_pending = dp
                    bottleneck_id = step["id"]

        if bottleneck_id:
            for step in steps:
                if step["id"] == bottleneck_id:
                    step["is_bottleneck"] = True
                    break

        return {
            "timeline": steps,
            "bottleneck_id": bottleneck_id,
            "total": len(steps),
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
