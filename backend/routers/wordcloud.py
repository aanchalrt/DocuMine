"""
Word cloud router — /api/wordcloud
Returns keyword/weight pairs derived from document text via Gemini.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from services import firestore_service, gemini_service

router = APIRouter()


# ---------------------------------------------------------------------------
# GET /api/wordcloud/data
# ---------------------------------------------------------------------------

@router.get("/data")
async def get_word_cloud_data(
    doc_ids: Optional[str] = Query(
        None,
        description="Comma-separated document IDs. Omit to use all documents.",
    ),
):
    """
    Return top keyword/weight pairs for building a word cloud.

    Query params:
        doc_ids: optional comma-separated list of document IDs to filter.
    """
    try:
        all_docs = firestore_service.get_all_documents()

        if doc_ids:
            requested_ids = {d.strip() for d in doc_ids.split(",") if d.strip()}
            selected_docs = [d for d in all_docs if d.get("id") in requested_ids]
        else:
            selected_docs = all_docs

        if not selected_docs:
            return {"keywords": [], "doc_count": 0}

        texts = [d.get("raw_text") or "" for d in selected_docs]
        keywords = gemini_service.get_word_cloud_data(texts)

        return {
            "keywords": keywords,
            "doc_count": len(selected_docs),
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
