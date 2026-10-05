"""
Reports router — /api/reports
Generates mine status summary reports and offers DOCX download.
"""
from __future__ import annotations

import io
import re
from typing import Literal

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from services import firestore_service, gemini_service

router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class ReportRequest(BaseModel):
    doc_ids: list[str]
    report_type: str = "mine_status_summary"


class DownloadRequest(BaseModel):
    report_html: str
    format: Literal["docx", "pdf"] = "docx"


# ---------------------------------------------------------------------------
# POST /api/reports/generate
# ---------------------------------------------------------------------------

@router.post("/generate")
async def generate_report(request: ReportRequest):
    """Fetch requested documents and generate an HTML report via Gemini."""
    if not request.doc_ids:
        raise HTTPException(status_code=400, detail="doc_ids must not be empty.")

    try:
        doc_data: list[dict] = []
        for doc_id in request.doc_ids:
            try:
                doc_data.append(firestore_service.get_document(doc_id))
            except KeyError:
                pass  # Skip missing docs silently

        if not doc_data:
            raise HTTPException(status_code=404, detail="No documents found for the given IDs.")

        report_html = gemini_service.generate_report(doc_data, request.report_type)

        # Extract citation tags from the generated HTML for structured response
        citation_pattern = re.compile(
            r'<citation\s+doc_id="([^"]+)"\s+field="([^"]+)"\s*/>'
        )
        citations = [
            {"doc_id": m.group(1), "field": m.group(2)}
            for m in citation_pattern.finditer(report_html)
        ]

        # Audit
        firestore_service.save_audit_entry(
            {
                "action": "report_generated",
                "user_role": "analyst",
                "details": (
                    f"Report type: {request.report_type}, "
                    f"doc_ids: {', '.join(request.doc_ids)}"
                ),
            }
        )

        return {
            "report_html": report_html,
            "citations": citations,
            "doc_count": len(doc_data),
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# POST /api/reports/download
# ---------------------------------------------------------------------------

@router.post("/download")
async def download_report(request: DownloadRequest):
    """
    Convert an HTML report string into a downloadable DOCX file.
    Strips HTML tags and maps headings to python-docx heading styles.
    """
    try:
        from docx import Document  # type: ignore
        from docx.shared import Pt  # type: ignore

        document = Document()
        document.core_properties.title = "DocuMine Report"

        # Simple HTML → DOCX converter
        _html_to_docx(document, request.report_html)

        buffer = io.BytesIO()
        document.save(buffer)
        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type=(
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ),
            headers={
                "Content-Disposition": 'attachment; filename="documine_report.docx"'
            },
        )

    except ImportError as exc:
        raise HTTPException(
            status_code=501,
            detail="python-docx is not installed.",
        ) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Internal HTML → DOCX helper
# ---------------------------------------------------------------------------

def _html_to_docx(document, html: str) -> None:
    """
    Naïve HTML-to-DOCX converter.
    Maps h1–h3 to Heading styles, <p> / <li> to Normal paragraphs.
    Strips all other tags.
    """
    import re as _re

    # Split on block-level tags while keeping delimiters
    token_pattern = _re.compile(
        r"(<h[1-3][^>]*>.*?</h[1-3]>|<p[^>]*>.*?</p>|<li[^>]*>.*?</li>)",
        _re.IGNORECASE | _re.DOTALL,
    )

    tag_strip = _re.compile(r"<[^>]+>")
    heading_tag = _re.compile(r"<h([1-3])", _re.IGNORECASE)

    tokens = token_pattern.split(html)

    for token in tokens:
        token = token.strip()
        if not token:
            continue

        h_match = heading_tag.match(token)
        clean_text = tag_strip.sub("", token).strip()
        if not clean_text:
            continue

        if h_match:
            level = int(h_match.group(1))
            document.add_heading(clean_text, level=level)
        elif token.lower().startswith("<li"):
            para = document.add_paragraph(style="List Bullet")
            para.add_run(clean_text)
        else:
            document.add_paragraph(clean_text)
