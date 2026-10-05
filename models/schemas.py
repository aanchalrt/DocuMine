"""
Pydantic v2 schemas for DocuMine API.
All models use model_config for strict validation where appropriate.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


# ---------------------------------------------------------------------------
# DocumentField
# ---------------------------------------------------------------------------

class DocumentField(BaseModel):
    """Represents a single extracted field from a document."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    doc_id: str
    name: str
    value: str
    unit: str = ""
    confidence: float = Field(ge=0.0, le=1.0)
    flag: Optional[str] = None  # 'needs_review' when confidence < 0.6
    source: str = ""

    @model_validator(mode="after")
    def auto_flag(self) -> "DocumentField":
        """Automatically set flag to 'needs_review' when confidence < 0.6."""
        if self.confidence < 0.6 and not self.flag:
            self.flag = "needs_review"
        return self


# ---------------------------------------------------------------------------
# ExtractedDocument
# ---------------------------------------------------------------------------

DocType = Literal[
    "geological_report",
    "production_log",
    "compliance_report",
    "correspondence",
    "archived",
    "general",
]


class ExtractedDocument(BaseModel):
    """Top-level document stored after extraction + AI field parsing."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    filename: str
    doc_type: DocType = "general"
    mine_name: str = ""
    upload_timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
    fields: List[DocumentField] = Field(default_factory=list)
    raw_text: str = ""


# ---------------------------------------------------------------------------
# ConflictRecord
# ---------------------------------------------------------------------------

ConflictType = Literal[
    "unexplained_variance",
    "method_change",
    "sum_mismatch",
    "low_confidence",
]

Severity = Literal["high", "medium", "low"]


class ConflictRecord(BaseModel):
    """A detected data conflict across one or more documents."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    parameter: str
    conflict_type: ConflictType
    severity: Severity
    values: List[dict] = Field(default_factory=list)
    note: str = ""
    detected_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )


# ---------------------------------------------------------------------------
# AuditEntry
# ---------------------------------------------------------------------------

AuditAction = Literal[
    "document_uploaded",
    "report_generated",
    "query_asked",
    "conflict_flagged",
    "document_approved",
]


class AuditEntry(BaseModel):
    """An immutable audit log record."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    action: AuditAction
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
    user_role: str = "system"
    doc_id: Optional[str] = None
    details: Optional[str] = None


# ---------------------------------------------------------------------------
# ChatMessage
# ---------------------------------------------------------------------------

Language = Literal["en", "hi"]


class ChatMessage(BaseModel):
    """A single message in the chat interface."""

    role: Literal["user", "assistant"]
    content: str
    language: Language = "en"
    citations: List[dict] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# ClearanceStep
# ---------------------------------------------------------------------------

ClearanceStatus = Literal["pending", "resolved", "escalated"]


class ClearanceStep(BaseModel):
    """One step in the regulatory clearance / NOC pipeline."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    doc_id: str
    sender_office: str = ""
    recipient_office: str = ""
    date: str = ""
    subject: str = ""
    status: ClearanceStatus = "pending"
    days_pending: Optional[int] = None


# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------

class ReportRequest(BaseModel):
    """Request body for report generation."""

    doc_ids: List[str]
    report_type: str = "mine_status_summary"


class ChatRequest(BaseModel):
    """Request body for chat queries."""

    question: str
    previous_interaction_id: Optional[str] = None
