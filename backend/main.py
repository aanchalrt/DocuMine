"""
DocuMine API — main entry point.
Starts FastAPI with CORS middleware, all routers, and automatic seed ingestion
on first startup (when the Firestore documents collection is empty).
"""
from __future__ import annotations

import os
from dotenv import load_dotenv
load_dotenv()
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
from routers import audit, chat, clearance, ingest, reports, validation, wordcloud


# ---------------------------------------------------------------------------
# Lifespan — runs once on startup / shutdown
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    On startup, auto-ingest seed data if the documents collection is empty.
    Failures are caught and logged so they never block the server from starting.
    """
    try:
        from services.firestore_service import get_all_documents
        from services.seed_ingestor import ingest_seed_data

        docs = get_all_documents()
        if len(docs) == 0:
            print("[startup] Documents collection is empty — running seed ingestion…")
            ingested = await ingest_seed_data()
            print(f"[startup] Seed ingestion complete — {len(ingested)} document(s) ingested.")
        else:
            print(f"[startup] {len(docs)} document(s) already in Firestore — skipping seed ingestion.")
    except Exception as exc:  # noqa: BLE001
        print(f"[startup] Seed ingestion skipped: {exc}")

    yield  # ← application runs here

    # Shutdown hook (nothing needed currently)
    print("[shutdown] DocuMine API shutting down.")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="DocuMine API",
    version="1.0.0",
    description=(
        "AI-powered document analysis backend for coal mining regulatory documents. "
        "Developed for Government of India / PSU sector use."
    ),
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(ingest.router,     prefix="/api/ingest",     tags=["ingest"])
app.include_router(reports.router,    prefix="/api/reports",    tags=["reports"])
app.include_router(wordcloud.router,  prefix="/api/wordcloud",  tags=["wordcloud"])
app.include_router(chat.router,       prefix="/api/chat",       tags=["chat"])
app.include_router(validation.router, prefix="/api/validation", tags=["validation"])
app.include_router(audit.router,      prefix="/api/audit",      tags=["audit"])
app.include_router(clearance.router,  prefix="/api/clearance",  tags=["clearance"])


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/api/health", tags=["health"])
async def health():
    """Simple liveness probe."""
    return {"status": "ok", "service": "DocuMine API"}


# ---------------------------------------------------------------------------
# Dev entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),
        reload=True,
    )
