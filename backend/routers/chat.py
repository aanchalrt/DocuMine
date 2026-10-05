"""
Chat router — /api/chat
Answers questions about the document corpus using Gemini with citations.
"""
from __future__ import annotations

from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services import firestore_service, gemini_service

router = APIRouter()


# ---------------------------------------------------------------------------
# Request model
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    question: str
    previous_interaction_id: Optional[str] = None


# ---------------------------------------------------------------------------
# POST /api/chat/query
# ---------------------------------------------------------------------------

@router.post("/query")
async def chat_query(request: ChatRequest):
    """
    Answer a natural-language question grounded in the document corpus.

    Supports English and Hindi (Devanagari auto-detection).
    Returns answer text, detected language, citation list, and an interaction ID
    for future reference.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    try:
        # Fetch all documents (raw_text + fields)
        documents = firestore_service.get_all_documents()

        if not documents:
            return {
                "answer": (
                    "No documents have been ingested yet. "
                    "Please upload documents before querying."
                ),
                "language": "en",
                "citations": [],
                "interaction_id": str(uuid4()),
            }

        # Ask Gemini
        result = gemini_service.chat_query(
            question=request.question,
            documents=documents,
            previous_interaction_id=request.previous_interaction_id,
        )

        interaction_id = str(uuid4())

        # Audit
        firestore_service.save_audit_entry(
            {
                "action": "query_asked",
                "user_role": "analyst",
                "details": (
                    f"Question: {request.question[:200]} | "
                    f"Language: {result.get('language', 'en')}"
                ),
            }
        )

        return {
            "answer": result.get("answer", ""),
            "language": result.get("language", "en"),
            "citations": result.get("citations", []),
            "interaction_id": interaction_id,
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
